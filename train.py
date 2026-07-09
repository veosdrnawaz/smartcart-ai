import os
import sys

# Add backend directory to Python path to import its modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from generate_data import generate_transactions
    from train_model import train_association_model
except ImportError as e:
    print(f"Error: Unable to import backend scripts. Ensure the 'backend' folder exists. Details: {e}")
    sys.exit(1)

def main():
    print("=" * 60)
    print(" SmartCart AI - Model Training Runner")
    print("=" * 60)
    
    # Define root-level paths
    data_dir = os.path.join(current_dir, "data")
    models_dir = os.path.join(current_dir, "models")
    
    # Ensure folders exist
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    csv_path = os.path.join(data_dir, "transactions.csv")
    model_path = os.path.join(models_dir, "model.pkl")
    
    # 1. Check if dataset exists, generate if missing
    if not os.path.exists(csv_path):
        print(f"[*] Dataset not found at {csv_path}. Synthesizing dataset...")
        generate_transactions(csv_path)
    else:
        print(f"[+] Dataset located at {csv_path}.")
        
    # 2. Train and save association rules model
    print(f"[*] Starting Apriori Association Rules training...")
    try:
        train_association_model(csv_path, model_path)
        print(f"[+] Model successfully trained and saved to {model_path}.")
        
        # Keep a copy in backend for Vercel/legacy support
        backend_model_path = os.path.join(backend_dir, "model.pkl")
        backend_csv_path = os.path.join(backend_dir, "transactions.csv")
        
        import shutil
        shutil.copy(model_path, backend_model_path)
        shutil.copy(csv_path, backend_csv_path)
        print(f"[+] Copied model and dataset backups to backend/ for serverless hosting.")
    except Exception as e:
        print(f"[-] Training failed: {e}")
        sys.exit(1)
        
    print("=" * 60)
    print(" Model Training Completed Successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()
