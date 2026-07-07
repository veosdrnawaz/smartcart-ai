import os
import pickle
import pandas as pd

def load_rules(model_path):
    """
    Loads the association rules from the pickle file.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please run train_model.py first.")
        
    with open(model_path, "rb") as f:
        rules = pickle.load(f)
    return rules

def get_recommendations(product_name, rules_df, confidence_threshold=0.60):
    """
    Given a product name, find recommendations from rules where the product is the antecedent.
    Filters by confidence threshold, unpacks multi-item consequents, deduplicates,
    and sorts by Lift, Confidence, and Support in descending order.
    """
    if rules_df is None or rules_df.empty:
        return []

    recommendations_map = {}

    # Iterate through each rule
    for _, rule in rules_df.iterrows():
        antecedents = rule['antecedents']
        
        # Check if the product is in the antecedents
        # We focus on rules where the antecedent contains the product.
        # To make it most relevant for single product pages, we check if the antecedent is exactly the product.
        if len(antecedents) == 1 and product_name in antecedents:
            consequents = rule['consequents']
            confidence = float(rule['confidence'])
            lift = float(rule['lift'])
            support = float(rule['support'])
            
            # Skip rules that don't meet the confidence threshold
            if confidence < confidence_threshold:
                continue
                
            # For each item in the consequents, add it to recommendations
            for item in consequents:
                # If the item is already recommended, keep the one with better metrics
                # (Priority: Lift -> Confidence -> Support)
                if item in recommendations_map:
                    existing = recommendations_map[item]
                    if (lift > existing['lift']) or \
                       (lift == existing['lift'] and confidence > existing['confidence']) or \
                       (lift == existing['lift'] and confidence == existing['confidence'] and support > existing['support']):
                        recommendations_map[item] = {
                            "item": item,
                            "confidence": round(confidence, 4),
                            "lift": round(lift, 4),
                            "support": round(support, 4)
                        }
                else:
                    recommendations_map[item] = {
                        "item": item,
                        "confidence": round(confidence, 4),
                        "lift": round(lift, 4),
                        "support": round(support, 4)
                    }

    # Convert map to list
    recommendations_list = list(recommendations_map.values())

    # Sort recommendations by Lift (desc), Confidence (desc), Support (desc)
    recommendations_list.sort(key=lambda x: (-x['lift'], -x['confidence'], -x['support']))

    return recommendations_list

if __name__ == "__main__":
    # Quick CLI test
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_file = os.path.join(current_dir, "model.pkl")
    
    try:
        rules = load_rules(model_file)
        test_product = "Laptop"
        recs = get_recommendations(test_product, rules)
        print(f"Recommendations for '{test_product}':")
        for r in recs:
            print(f" - {r['item']}: Confidence={r['confidence']}, Lift={r['lift']}, Support={r['support']}")
    except Exception as e:
        print(f"Error testing recommendations: {e}")
