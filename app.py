from flask import Flask, jsonify, request
from flask_cors import CORS
from pso.utils import fetch_items_and_knapsacks  
from pso.model import particle_swarm_optimization 
from pso.model import Knapsack
from config import DB_CONFIG
import mysql.connector  

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
@app.route("/output", methods=["POST"])
def optimize_products():
    data = request.get_json()
    
    max_total_price = float(data.get("max_total_price", 0))  
    max_total_weight = float(data.get("max_total_weight", 0)) 
    
    # Validasi input
    if max_total_price <= 0 or max_total_weight <= 0:
        return jsonify({"error": "Budget dan berat harus > 0"}), 400

    items, _ = fetch_items_and_knapsacks() 
    
    feasible_items = [
        item for item in items 
        if item.price <= max_total_price and item.weight <= max_total_weight
    ]
    
    if not feasible_items:
        return jsonify({"error": "Tidak ada item yang memenuhi budget/berat"}), 400

    knapsack = Knapsack(capacity=max_total_weight, budget=max_total_price)
    
    solution_sets = particle_swarm_optimization(
        feasible_items,
        knapsack,
        num_particles=100,
        num_iterations=200,
        top_n=3
    )

    result = {"parcels": []}
    for idx, items_in_parcel in enumerate(solution_sets, 1):
        result["parcels"].append({
            "parcel_number": idx,
            "total_price": sum(item.price for item in items_in_parcel), 
            "total_value": sum(item.value for item in items_in_parcel),  
            "total_weight": sum(item.weight for item in items_in_parcel),  
            "items": [
                {
                    "category": item.category,
                    "name": item.name,
                    "price": item.price, 
                    "weight": item.weight,  
                    "value": item.value
          }
                for item in items_in_parcel
            ]
        })

    return jsonify(result)  

if __name__ == "__main__":
    app.run(debug=False)
