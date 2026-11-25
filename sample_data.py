
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

products = {
    "Laptop": ("Electronics", 55000, 42000),
    "Mouse": ("Accessories", 500, 250),
    "Keyboard": ("Accessories", 1200, 650),
    "Monitor": ("Electronics", 12000, 8500),
    "Headphones": ("Accessories", 2500, 1400),
    "Printer": ("Electronics", 15000, 11000),
    "Desk": ("Furniture", 8000, 5500),
    "Chair": ("Furniture", 6000, 4000)
}

regions = ["North", "South", "East", "West"]
sales_reps = ["Aman", "Rahul", "Priya", "Neha", "Rohit"]

customers = [
    "Customer A", "Customer B", "Customer C",
    "Customer D", "Customer E", "Customer F"
]

rows = []

for i in range(1, 301):
    product = random.choice(list(products.keys()))
    category, price, cost = products[product]

    order_date = datetime(2026, 1, 1) + timedelta(
        days=random.randint(0, 300)
    )

    rows.append({
        "order_id": f"ORD{i:04d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "product": product,
        "category": category,
        "region": random.choice(regions),
        "quantity": random.randint(1, 10),
        "unit_price": price,
        "unit_cost": cost,
        "sales_rep": random.choice(sales_reps),
        "customer": random.choice(customers)
    })

# Add a duplicate record to test data cleaning
rows.append(rows[0].copy())

# Add a missing region to test data cleaning
rows[5]["region"] = ""

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

file_path = data_dir / "sample_sales_data.csv"

with open(file_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Sample dataset created successfully!")
print(f"Total records: {len(rows)}")
print(f"File location: {file_path}")
