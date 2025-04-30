from flask import Flask, jsonify, request
from flask_cors import CORS
from pso.utils import fetch_items_and_knapsacks  # Pastikan fungsi ini ada
from pso.model import particle_swarm_optimization  # Fungsi optimasi
from config import DB_CONFIG
import mysql.connector  # Pastikan sudah terinstall

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

# Route utama
@app.route("/output", methods=["POST"])
def optimize_products():
    data = request.get_json()
    max_total_price = float(data.get("max_total_price", 0))
    max_total_weight = float(data.get("max_total_weight", 0))

    # Ambil data item dan knapsacks dari database
    items, knapsacks = fetch_items_and_knapsacks()

    # Filter item yang memenuhi batas harga dan berat
    filtered_items = [
        item for item in items
        if item.price <= max_total_price and item.weight <= max_total_weight
    ]

    if not filtered_items:
        return jsonify({
            "error": "Tidak ada item yang memenuhi batas harga/berat",
            "max_price": max_total_price,
            "max_weight": max_total_weight
        }), 400

    # Jalankan algoritma PSO
    solution_sets = particle_swarm_optimization(
        filtered_items,
        knapsacks,
        num_particles=100,
        num_iterations=1000,
        top_n=3  
    )

    # Susun hasil untuk dikembalikan ke frontend
    result = {
        "parcels": []
    }

    for idx, solution in enumerate(solution_sets, 1):
        parcel_data = {
            "parcel_number": idx,
            "knapsacks": [
                {
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
                for i, k in enumerate(solution)
            ],
            "total_value": sum(k.total_value() for k in solution)
        }
        result["parcels"].append(parcel_data)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
