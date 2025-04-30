import mysql.connector
from config import DB_CONFIG
from pso.model import Item, Knapsack

def fetch_items_and_knapsacks():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # Ambil data produk
    cursor.execute("SELECT * FROM barang")
    items = [
        Item(row['kategori_nama'], row['nama_barang'], row['harga_umum'], row['berat'])
        for row in cursor.fetchall()
    ]

    # Ambil data knapsack (misal tabel bernama bin)
    cursor.execute("SELECT * FROM knapsack")
    knapsacks = [
        Knapsack(row['capacity'], row['budget'])
        for row in cursor.fetchall()
    ]

    conn.close()
    return items, knapsacks
