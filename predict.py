import os
import sys
import argparse

# Add backend directory to Python path to import its modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from recommend import load_rules, get_recommendations
except ImportError as e:
    print(f"Error: Unable to import recommendation module. Details: {e}")
    sys.exit(1)

# Recognized product list (for user assistance)
VALID_PRODUCTS = [
    "Laptop", "Mouse", "Laptop Bag", "Keyboard",
    "Smartphone", "Charger", "Screen Protector", "Earbuds",
    "DSLR", "SD Card", "Tripod", "Camera Bag"
]

def main():
    parser = argparse.ArgumentParser(description="SmartCart AI CLI Recommendation Engine")
    parser.add_argument(
        "--product", 
        type=str, 
        help="Name of the product in the cart (e.g., 'Laptop', 'Smartphone', 'DSLR')"
    )
    parser.add_argument(
        "--confidence", 
        type=float, 
        default=0.60, 
        help="Confidence threshold for association rules (default: 0.60)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print(" SmartCart AI - Real-time Recommendation Inference CLI")
    print("=" * 60)

    # 1. Resolve model file path
    model_path = os.path.join(current_dir, "models", "model.pkl")
    fallback_path = os.path.join(backend_dir, "model.pkl")
    
    selected_model_path = model_path if os.path.exists(model_path) else fallback_path
    
    if not os.path.exists(selected_model_path):
        print(f"[-] Error: Serialized rules model not found at {model_path} or {fallback_path}.")
        print("[-] Please run 'python train.py' first to train the model.")
        sys.exit(1)
        
    # 2. Load model
    try:
        rules_df = load_rules(selected_model_path)
    except Exception as e:
        print(f"[-] Failed to load model rules: {e}")
        sys.exit(1)

    # 3. Handle product input
    product = args.product
    if not product:
        print("[*] Available catalog items in training database:")
        for idx, item in enumerate(VALID_PRODUCTS, 1):
            print(f"  {idx}. {item}")
        print("-" * 60)
        try:
            choice = input("Enter product name (or number from list above): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(VALID_PRODUCTS):
                product = VALID_PRODUCTS[int(choice) - 1]
            else:
                product = choice
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Canceled.")
            sys.exit(0)

    if not product or product.strip() == "":
        print("[-] Error: Product name cannot be empty.")
        sys.exit(1)

    product = product.strip()
    
    # 4. Standardize / check recognized items (case-insensitive fallback)
    matched_product = None
    for p in VALID_PRODUCTS:
        if p.lower() == product.lower():
            matched_product = p
            break
            
    if not matched_product:
        matched_product = product
        print(f"[!] Warning: '{product}' is not in the standard inventory catalog.")
        print("[*] Will check model rules anyway...")

    # 5. Run inference
    print(f"[*] Querying association rules for antecedent: [{matched_product}]")
    print(f"[*] Parameters: Min Confidence = {args.confidence}")
    print("-" * 60)

    try:
        recommendations = get_recommendations(matched_product, rules_df, confidence_threshold=args.confidence)
        
        if not recommendations:
            print(f"[!] No recommendations found matching the confidence threshold of {args.confidence}.")
            print("[*] Try lowering the confidence threshold (e.g., --confidence 0.40) or training on more data.")
        else:
            print(f"[+] Found {len(recommendations)} recommendation rules:")
            print("\n{:<18} | {:<10} | {:<8} | {:<8}".format("Recommended Item", "Confidence", "Lift", "Support"))
            print("-" * 52)
            for rec in recommendations:
                print("{:<18} | {:<10} | {:<8} | {:<8}".format(
                    rec['item'], 
                    f"{rec['confidence']*100:.1f}%", 
                    f"{rec['lift']:.2f}", 
                    f"{rec['support']:.2f}"
                ))
            print("-" * 52)
            print("[Info] Lift > 1.0 indicates a strong positive association (items frequently bought together).")
    except Exception as e:
        print(f"[-] Recommendation query failed: {e}")
        sys.exit(1)

    print("=" * 60)

if __name__ == "__main__":
    main()
