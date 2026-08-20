import os
import ast
import operator
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/calculator_db")
client = MongoClient(MONGO_URI)
db = client.get_database()
history_col = db["history"]

# Safe Expression Evaluator (Avoids unsafe eval())
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def evaluate_node(node):
    if isinstance(node, ast.Expression):
        return evaluate_node(node.body)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Invalid constant type")
    elif isinstance(node, ast.BinOp):
        left = evaluate_node(node.left)
        right = evaluate_node(node.right)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            if op_type == ast.Div and right == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return ALLOWED_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        operand = evaluate_node(node.operand)
        op_type = type(node.op)
        if op_type in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    else:
        raise ValueError("Unsupported expression syntax")

def safe_calculate(expression: str):
    parsed = ast.parse(expression, mode='eval')
    return evaluate_node(parsed)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json() or {}
    expr = data.get("expression", "").strip()

    if not expr:
        return jsonify({"error": "No expression provided"}), 400

    try:
        result = safe_calculate(expr)
        
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 8)

        record = {
            "expression": expr,
            "result": result,
            "timestamp": datetime.now(timezone.utc)
        }
        inserted = history_col.insert_one(record)

        return jsonify({
            "id": str(inserted.inserted_id),
            "expression": expr,
            "result": result
        }), 200

    except ZeroDivisionError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Invalid mathematical expression"}), 400

@app.route("/api/history", methods=["GET"])
def get_history():
    records = list(history_col.find().sort("timestamp", -1).limit(20))
    formatted = [
        {
            "id": str(r["_id"]),
            "expression": r["expression"],
            "result": r["result"],
            "timestamp": r["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if "timestamp" in r else ""
        }
        for r in records
    ]
    return jsonify(formatted), 200

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    history_col.delete_many({})
    return jsonify({"message": "History cleared successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
