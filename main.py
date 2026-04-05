from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def error(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

def validate(a, b):
    try:
        return float(a), float(b), None
    except (TypeError, ValueError):
        return None, None, error("Both 'a' and 'b' must be valid numbers")

@app.route("/")
def index():
    url = ""
    try:
        with open("server_url.txt") as f:
            url = f.read().strip()
    except FileNotFoundError:
        pass
    return jsonify({
        "status": "running",
        "public_url": url,
        "endpoints": ["/add", "/subtract", "/multiply", "/divide", "/power", "/modulo"]
    })

@app.route("/add")
def add():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    return jsonify({"success": True, "operation": "addition", "a": a, "b": b, "result": a + b})

@app.route("/subtract")
def subtract():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    return jsonify({"success": True, "operation": "subtraction", "a": a, "b": b, "result": a - b})

@app.route("/multiply")
def multiply():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    return jsonify({"success": True, "operation": "multiplication", "a": a, "b": b, "result": a * b})

@app.route("/divide")
def divide():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    if b == 0: return error("Cannot divide by zero")
    return jsonify({"success": True, "operation": "division", "a": a, "b": b, "result": a / b})

@app.route("/power")
def power():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    return jsonify({"success": True, "operation": "power", "a": a, "b": b, "result": a ** b})

@app.route("/modulo")
def modulo():
    a, b, err = validate(request.args.get("a"), request.args.get("b"))
    if err: return err
    if b == 0: return error("Cannot modulo by zero")
    return jsonify({"success": True, "operation": "modulo", "a": a, "b": b, "result": a % b})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
