import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add current directory to path to ensure modules are loaded correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from recommend import load_rules, get_recommendations

app = Flask(__name__)
# Enable CORS for all routes and origins (important for Vercel static hosting to connect)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global rules DataFrame reference
rules_df = None
model_path = os.path.join(current_dir, "model.pkl")

# Helper list of valid products to check for invalid products
VALID_PRODUCTS = {
    # Primary items
    "Laptop", "Mouse", "Laptop Bag", "Keyboard",
    "Smartphone", "Charger", "Screen Protector", "Earbuds",
    "DSLR", "SD Card", "Tripod", "Camera Bag",
    # Noise/Extra items
    "Monitor", "USB Hub", "HDMI Cable", "Printer", "Tablet", 
    "Gaming Mouse", "Mechanical Keyboard", "Power Bank", "Smart Watch", 
    "Router", "SSD", "Headphones", "Microphone", "Ring Light", "Webcam"
}

def init_model():
    """
    Attempts to load the model.pkl file.
    Does not crash the app if missing, allowing the server to start
    and report the health error properly.
    """
    global rules_df
    try:
        if os.path.exists(model_path):
            rules_df = load_rules(model_path)
            print("Model loaded successfully at startup.")
        else:
            print(f"Warning: Model file not found at {model_path}. Please run train_model.py.")
    except Exception as e:
        print(f"Error loading model at startup: {e}")

# Initialize model
init_model()

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    Also returns status of model file availability.
    """
    model_loaded = rules_df is not None
    return jsonify({
        "status": "healthy" if model_loaded else "degraded",
        "message": "SmartCart AI API is running.",
        "model_loaded": model_loaded,
        "dataset_exists": os.path.exists(os.path.join(current_dir, "transactions.csv"))
    }), 200

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Recommendation API.
    Input JSON:
    {
      "product": "Laptop"
    }
    """
    global rules_df
    
    # 1. Handle API/System Failures: Check if model is loaded
    if rules_df is None:
        # Try to reload in case it was generated after startup
        init_model()
        if rules_df is None:
            return jsonify({
                "error": "Missing model configuration",
                "message": "The association rules model has not been trained or is missing. Please contact administrator."
            }), 500

    try:
        # Parse and validate request JSON
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "error": "Empty input",
                "message": "Invalid request body. Expected JSON data."
            }), 400
            
        product = data.get("product")
        
        # 2. Handle empty input
        if not product or str(product).strip() == "":
            return jsonify({
                "error": "Empty input",
                "message": "The product parameter is required and cannot be empty."
            }), 400
            
        product = str(product).strip()
        
        # 3. Handle invalid product names
        # Normalize casing to match VALID_PRODUCTS (case-insensitive checks can be done, but let's standardise on exact spelling)
        # Find matches by case-insensitive check to be user-friendly, then use the official casing
        matched_product = None
        for p in VALID_PRODUCTS:
            if p.lower() == product.lower():
                matched_product = p
                break
                
        if not matched_product:
            return jsonify({
                "error": "Invalid product",
                "message": f"'{product}' is not a recognized product in our inventory catalog."
            }), 400
            
        # Get recommendations
        recommendations = get_recommendations(matched_product, rules_df)
        
        return jsonify({
            "product": matched_product,
            "recommendations": recommendations
        }), 200

    except Exception as e:
        return jsonify({
            "error": "API failure",
            "message": f"An unexpected error occurred while processing recommendations: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Run server locally on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
