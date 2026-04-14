# backend/app.py
from flask import Flask, request, jsonify
from equilibrium import bubble_point

app = Flask(__name__)

@app.route("/bubble", methods=["POST"])
def bubble():

    data = request.json

    T = data["T"]
    comp_ids = data["components"]
    x = data["x"]
    model = data["model"]
    params = data.get("params", {})

    try:
        P = bubble_point(T, comp_ids, x, model, params)

        return jsonify({
            "status": "success",
            "pressure": P
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

@app.route('/')
def home():
    return "API Thermodynamique en marche 🚀"
if __name__ == "__main__":
    app.run(debug=True)