# pso/utils.py
import mysql.connector
from config import DB_CONFIG
from pso.model import Item, Knapsack

def fetch_items_and_knapsacks():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # Ambil data produk
    cursor.execute("SELECT * FROM barang")
    items = [
        Item(
            category=row['kategori_nama'],
            name=row['nama_barang'],
            price=float(row['harga_umum']),
            weight=float(row['berat'])
        )
        for row in cursor.fetchall()
    ]

    # Ambil data knapsack
    cursor.execute("SELECT * FROM knapsack")
    knapsacks = [
        Knapsack(
            capacity=float(row['capacity']),
            budget=float(row['budget']))
        for row in cursor.fetchall()
    ]

    conn.close()
    return items, knapsacks