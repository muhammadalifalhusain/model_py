from flask import Flask, jsonify, request
from flask_cors import CORS
from pso.utils import fetch_items_and_knapsacks  # Pastikan fetch_items_and_knapsacks menyesuaikan inputan
from pso.model import particle_swarm_optimization  # Sesuaikan dengan fungsi optimasi Anda
from config import DB_CONFIG
import mysql.connector  # Pastikan ini ada



app = Flask(__name__)
CORS(app)

def get_db_connection():
    connection = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )
    return connection

@app.route("/optimize", methods=["POST"])
def optimize_products():
    data = request.get_json()

    max_total_price = data.get("max_total_price", None)
    max_total_weight = data.get("max_total_weight", None)

    if max_total_price is None or max_total_weight is None:
        return jsonify({"error": "Missing required parameters: max_total_price or max_total_weight"}), 400

    # Ambil data produk dan knapsack dari database
    items, knapsacks = fetch_items_and_knapsacks()

    # Set filter berdasarkan input dari user
    for item in items:
        if item.price > max_total_price or item.weight > max_total_weight:
            items.remove(item)

    # Proses optimasi dengan PSO
    solution, total_value = particle_swarm_optimization(items, knapsacks)

    # Menyiapkan hasil untuk dikirimkan ke frontend
    result = {
        "total_value": total_value,
        "knapsacks": []
    }

    for i, k in enumerate(solution):
        knapsack_data = {
            "index": i + 1,
            "total_weight": k.total_weight(),
            "total_price": k.total_price(),
            "items": [
                {
                    "category": item.category,
                    "name": item.name,
                    "price": item.price,
                    "weight": item.weight,
                    "value": item.value
                }
                for item in k.items
            ]
        }
        result["knapsacks"].append(knapsack_data)

    return jsonify(result)

@app.route("/products", methods=["GET"])
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM barang LIMIT 10")  
    products = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)
