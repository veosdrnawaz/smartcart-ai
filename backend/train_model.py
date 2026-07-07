import os
import pickle
import csv
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

def train_association_model(csv_path, model_path):
    """
    Loads transactions, applies Apriori to find frequent itemsets,
    generates association rules, and pickles the rules.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Transactions file not found at {csv_path}. Run generate_data.py first.")

    # 1. Read Transactions CSV
    transactions = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row: # Skip empty rows
                transactions.append(row)

    print(f"Loaded {len(transactions)} transactions for training.")

    # 2. One-hot encode the transactions
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    # 3. Apply Apriori algorithm
    # min_support = 0.05
    print("Running Apriori algorithm (min_support=0.05)...")
    frequent_itemsets = apriori(df, min_support=0.05, use_colnames=True)
    
    if frequent_itemsets.empty:
        print("Warning: No frequent itemsets found with min_support=0.05.")
        # Create an empty rules DataFrame with matching columns
        rules = pd.DataFrame(columns=[
            'antecedents', 'consequents', 'antecedent support', 
            'consequent support', 'support', 'confidence', 'lift', 
            'leverage', 'conviction', 'zhangs_metric'
        ])
    else:
        # 4. Generate association rules
        # metric = "lift", min_threshold = 1.2
        print("Generating association rules (metric='lift', min_threshold=1.2)...")
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.2)
        
    print(f"Generated {len(rules)} association rules.")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # 5. Save the rules to model.pkl
    with open(model_path, "wb") as f:
        pickle.dump(rules, f)
        
    print(f"Model saved successfully to {model_path}.")
    return rules

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "transactions.csv")
    model_file = os.path.join(current_dir, "model.pkl")
    train_association_model(csv_file, model_file)
