from flask import Flask, request, jsonify
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
app = Flask(__name__)

def compute_scores(data):
    blasts = data.get("blasts", 0)
    lymph = data.get("lymph", 0)
    myeloid = data.get("myeloid", 0)
    baso = data.get("baso", 0)

    markers = data.get("markers", [])
    morphology = data.get("morphology", [])

    scores = {
        "AML": 1,
        "ALL": 1,
        "CLL": 1,
        "CML": 1
    }

    # --- Bayesian-like weighting (pseudo LR multipliers) ---

    # AML
    if blasts >= 20:
        scores["AML"] *= 5
    if "MPO" in markers:
        scores["AML"] *= 6
    if "Auer rods" in morphology:
        scores["AML"] *= 10

    # ALL
    if blasts >= 20 and lymph > 40:
        scores["ALL"] *= 5
    if "TdT" in markers:
        scores["ALL"] *= 6
    if "CD19" in markers or "CD3" in markers:
        scores["ALL"] *= 4

    # CLL
    if lymph > 60:
        scores["CLL"] *= 5
    if "CD5" in markers and "CD23" in markers:
        scores["CLL"] *= 8
    if "smudge cells" in morphology:
        scores["CLL"] *= 6

    # CML
    if myeloid > 20:
        scores["CML"] *= 5
    if baso > 2:
        scores["CML"] *= 4
    if "BCR-ABL" in markers:
        scores["CML"] *= 10

    total = sum(scores.values())
    probs = {k: (v / total) * 100 for k, v in scores.items()}

    top = max(probs, key=probs.get)

    suggestions = {
        "AML": ["Check MPO, CD13, CD33", "Look for Auer rods"],
        "ALL": ["Check TdT, CD19/CD3", "Assess bone marrow"],
        "CLL": ["Check CD5+, CD23+", "Look for smudge cells"],
        "CML": ["Confirm BCR-ABL", "Assess phase (blast %)"]
    }

    return probs, top, suggestions[top]


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    probs, top, suggestion = compute_scores(data)

    return jsonify({
        "probabilities": probs,
        "most_likely": top,
        "next_steps": suggestion
    })


if __name__ == "__main__":
    app.run(debug=True)