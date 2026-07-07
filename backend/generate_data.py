import os
import random
import csv

def generate_transactions(output_path):
    """
    Generates exactly 500 realistic shopping transactions based on predefined conditional
    probabilities (bundling rules) and random noise items.
    """
    # Set seed for deterministic reproducibility
    random.seed(42)
    
    extra_items = [
        "Monitor", "USB Hub", "HDMI Cable", "Printer", "Tablet", 
        "Gaming Mouse", "Mechanical Keyboard", "Power Bank", "Smart Watch", 
        "Router", "SSD", "Headphones", "Microphone", "Ring Light", "Webcam"
    ]
    
    transactions = []
    
    # 1. Laptop Bundles (150 transactions)
    # Rules: Mouse (70%), Laptop Bag (60%), Keyboard (40%)
    for _ in range(150):
        basket = ["Laptop"]
        if random.random() < 0.70:
            basket.append("Mouse")
        if random.random() < 0.60:
            basket.append("Laptop Bag")
        if random.random() < 0.40:
            basket.append("Keyboard")
        
        # Add 0 to 2 random noisy items
        noise_count = random.randint(0, 2)
        if noise_count > 0:
            basket.extend(random.sample(extra_items, noise_count))
        transactions.append(basket)

    # 2. Smartphone Bundles (150 transactions)
    # Rules: Charger (85%), Screen Protector (80%), Earbuds (50%)
    for _ in range(150):
        basket = ["Smartphone"]
        if random.random() < 0.85:
            basket.append("Charger")
        if random.random() < 0.80:
            basket.append("Screen Protector")
        if random.random() < 0.50:
            basket.append("Earbuds")
            
        # Add 0 to 2 random noisy items
        noise_count = random.randint(0, 2)
        if noise_count > 0:
            basket.extend(random.sample(extra_items, noise_count))
        transactions.append(basket)

    # 3. DSLR Bundles (100 transactions)
    # Rules: SD Card (75%), Tripod (65%), Camera Bag (55%)
    for _ in range(100):
        basket = ["DSLR"]
        if random.random() < 0.75:
            basket.append("SD Card")
        if random.random() < 0.65:
            basket.append("Tripod")
        if random.random() < 0.55:
            basket.append("Camera Bag")
            
        # Add 0 to 2 random noisy items
        noise_count = random.randint(0, 2)
        if noise_count > 0:
            basket.extend(random.sample(extra_items, noise_count))
        transactions.append(basket)

    # 4. Miscellaneous Bundles (100 transactions)
    # Simulates random shopping carts of various sizes
    for _ in range(100):
        basket_size = random.randint(2, 5)
        basket = random.sample(extra_items, basket_size)
        transactions.append(basket)

    # Shuffle transactions list to distribute items realistically
    random.shuffle(transactions)

    # Ensure directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as CSV file (one transaction per row, comma-separated)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(transactions)
        
    print(f"Successfully generated {len(transactions)} transactions and saved to {output_path}.")
    return transactions

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "transactions.csv")
    generate_transactions(csv_file)
