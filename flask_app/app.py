"""
Flask Portfolio App — Inés G. Calvo
====================================
Routes:
  GET  /                  → Home (redirects to portal)
  GET  /cv                → Full CV page
  GET  /cv/download       → PDF download of CV (browser print dialog)
  GET  /projects          → Projects hub
  GET  /neuropapers       → Journal Prediction model UI
  POST /neuropapers       → Run prediction, return results
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

# ── Try to load the Neuropapers model ──────────────────────────────────────
MODEL_LOADED = False
_qda_model       = None
_label_encoder   = None

try:
    import joblib
    _model_dir = os.path.join(os.path.dirname(__file__), "model")
    _qda_model     = joblib.load(os.path.join(_model_dir, "qda_model.pkl"))
    _label_encoder = joblib.load(os.path.join(_model_dir, "label_encoder.pkl"))
    MODEL_LOADED = True
    print("✓ Neuropapers model loaded successfully.")
except Exception as e:
    print(f"⚠  Could not load Neuropapers model: {e}")
    print("   Place qda_model.pkl and label_encoder.pkl in flask_app/model/")


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    """Redirect root to the static GitHub Pages portal, or serve a mini landing."""
    return render_template("index.html")


@app.route("/cv")
def cv():
    """Full CV page."""
    return render_template("cv.html")


@app.route("/projects")
def projects():
    """Projects hub page."""
    return render_template("projects.html")


@app.route("/neuropapers", methods=["GET", "POST"])
def neuropapers():
    """
    GET  → Show the journal-prediction form.
    POST → Run the ML model and return top predictions.
    """
    results   = None
    error     = None
    title_val = ""
    abstr_val = ""

    if request.method == "POST":
        title_val = request.form.get("title", "").strip()
        abstr_val = request.form.get("abstract", "").strip()

        if not title_val or not abstr_val:
            error = "Please provide both a title and an abstract."
        elif not MODEL_LOADED:
            error = (
                "The model files are not yet installed on this server. "
                "See the README for instructions on adding qda_model.pkl and label_encoder.pkl."
            )
        else:
            try:
                from support_model import predict_journal_for_input
                raw = predict_journal_for_input(title_val, abstr_val, _qda_model, _label_encoder)
                # Sort by probability descending, take top 5
                results = sorted(raw, key=lambda x: x["probability"], reverse=True)[:5]
            except Exception as exc:
                error = f"Prediction failed: {exc}"

    return render_template(
        "neuropapers.html",
        results=results,
        error=error,
        model_loaded=MODEL_LOADED,
        title_val=title_val,
        abstr_val=abstr_val,
    )


# ── Run ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
