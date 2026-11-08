#!/usr/bin/env python3
"""
Provenance Guard — the web service.

Routes:
    POST /ping          the worked example. Don't edit it
    POST /submit        judge a piece of text
    POST /appeal        a writer disputes a decision
    POST /verify        a writer earns the verified-human credential (stretch)
    GET  /content/<id>  one item's current status (stretch)
    GET  /log           the audit log
    GET  /health        is the service up, and is the model loaded
"""

import uuid

from flask import Flask, jsonify, request

import audit
import config

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
class _LimiterOff:
    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── The build ─────────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """Take a piece of text, decide about it, log the decision, answer."""
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    creator_id = payload.get("creator_id", "unknown")

    if not isinstance(text, str) or not text.strip():
        audit.log_rejection(creator_id=creator_id, reason="missing_text")
        return jsonify({"error": "bad_request", "message": "Send JSON with a non-empty \"text\"."}), 400

    # Signal 1 - the model signal
    import detector
    try:
        model_score = detector.model_signal(text)
    except ValueError as exc:
        audit.log_rejection(creator_id=creator_id, reason="bad_input")
        return jsonify({"error": "bad_request", "message": str(exc)}), 400
    except detector.DetectorUnavailable as exc:
        audit.log_rejection(creator_id=creator_id, reason="detector_unavailable")
        return jsonify({"error": "detector_unavailable", "message": str(exc)}), 503

    # Signals 2 and 3, then combine (rule: scoring.py::combine_signals)
    import cues
    import scoring
    import stylometry

    style_score = stylometry.style_signal(text)
    cue_score = cues.cue_signal(text)
    word_count = len(stylometry.words(text))
    combined = scoring.combine_signals(model_score, style_score, word_count, cue_score)
    guess, label = scoring.score_to_label(combined)
    # confidence = distance from the uncertain middle: 0 = no idea, 1 = certain
    confidence = round(abs(combined - 0.5) * 2, 4)

    # Verified-human credential (stretch): shown on the work, never changes the score.
    verified = audit.is_verified(creator_id)

    content_id = f"c_{uuid.uuid4().hex[:12]}"
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined,
        guess=guess,
        label=label,
        status="decided",
        cue_score=cue_score,
        verified_human=verified,
    )

    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "confidence": confidence,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        "cue_score": cue_score,
        "combined_score": combined,
        "verified_human": verified,
    }), 200


@app.post("/appeal")
def appeal():
    """
    A writer says we got it wrong. Records the appeal beside the original
    decision and moves the item to under_review. No automatic re-checking.

    Expects JSON: {"content_id": "...", "reasoning": "..."}
    """
    payload = request.get_json(silent=True) or {}
    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "bad_request", "message": "Send JSON with a \"content_id\"."}), 400
    if not isinstance(reasoning, str) or not reasoning.strip():
        return jsonify({"error": "bad_request", "message": "Send JSON with your \"reasoning\"."}), 400

    history = audit.entries_for(content_id)
    if not history:
        return jsonify({"error": "not_found", "message": "No submission found with that content_id."}), 404

    # The creator comes from the original decision, not from the request.
    creator_id = history[0].get("creator_id", "unknown")
    audit.log_appeal(content_id=content_id, creator_id=creator_id, reasoning=reasoning)

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Thanks. Your appeal has been recorded and this work is now marked as under review.",
    }), 200


@app.post("/verify")
def verify():
    """
    Verified-human path (stretch). A writer earns a credential through an extra
    step: presenting the verification code. Work they submit afterwards carries
    verified_human: true. The credential is shown, it never changes the score.

    Expects JSON: {"creator_id": "...", "code": "..."}
    """
    payload = request.get_json(silent=True) or {}
    creator_id = payload.get("creator_id")
    code = payload.get("code")

    if not isinstance(creator_id, str) or not creator_id.strip() or creator_id == "unknown":
        return jsonify({"error": "bad_request", "message": "Send JSON with a real \"creator_id\"."}), 400
    if code != config.VERIFY_CODE:
        return jsonify({"error": "forbidden", "message": "That verification code is not valid."}), 403

    audit.log_verification(creator_id=creator_id, method="code")
    return jsonify({
        "creator_id": creator_id,
        "status": "verified_human",
        "message": "Verified. Work you submit from now on will show a verified-human credential.",
    }), 200


@app.get("/content/<content_id>")
def get_content(content_id):
    """Stretch: one item's current status, from the append-only log."""
    history = audit.entries_for(content_id)
    if not history:
        return jsonify({"error": "not_found", "message": "No submission found with that content_id."}), 404

    decision = next((e for e in history if "event" not in e), history[0])
    return jsonify({
        "content_id": content_id,
        "creator_id": decision.get("creator_id"),
        "status": history[-1].get("status"),
        "guess": decision.get("guess"),
        "label": decision.get("label"),
        "combined_score": decision.get("combined_score"),
        "verified_human": decision.get("verified_human", False),
        "appealed": any(e.get("event") == "appeal" for e in history),
    }), 200


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()