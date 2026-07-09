import os
import sys

# Add backend directory to Python path to import its modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app import app
except ImportError as e:
    print(f"Error: Unable to import backend Flask app. Details: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print(" SmartCart AI - Local Flask API Server Gateway")
    print("=" * 60)
    print("[*] Running API on port 5000...")
    print("[*] Local URL:   http://localhost:5000")
    print("[*] Health URL:  http://localhost:5000/health")
    print("[*] Recommend:   http://localhost:5000/recommend [POST]")
    print("[Info] Make sure you run 'python train.py' beforehand to train the model rules.")
    print("=" * 60)
    
    # Run the imported app
    app.run(host='0.0.0.0', port=5000, debug=True)
