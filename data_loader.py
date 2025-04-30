# pso/data_loader.py

import csv
from pso.model import Item, Knapsack

def fetch_items_and_knapsacks(items_csv_path, knapsack_csv_path):
    items = []
    knapsacks = []

    # Baca item dari CSV
    with open(items_csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            item = Item(
                name=row['Name'],
                price=float(row['Price']),
                weight=float(row['Weight']),
                value=float(row['Value']),
                category=row['Category']
            )
            items.append(item)

    # Baca knapsack dari CSV
    with open(knapsack_csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            knapsack = Knapsack(
                capacity=float(row['capacity']),
                budget=float(row['budget'])
            )
            knapsacks.append(knapsack)

    return items, knapsacks
