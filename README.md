# SmartCart AI - Market Basket Analysis & Product Recommendation Engine

SmartCart AI is a production-ready, E-commerce Cross-Selling Recommendation System that leverages Market Basket Analysis (MBA) and the **Apriori Algorithm** to predict and suggest products that are frequently bought together. It includes a Python ML backend, a Flask REST API, and a modern, responsive frontend built with glassmorphic HTML, CSS, and Vanilla JavaScript.

---

## 🏗️ Architecture Diagram

```
+--------------------------------------------------------------------------+
|                            1. OFFLINE TRAINING                           |
|                                                                          |
|  [generate_data.py] ---> (transactions.csv) ---> [train_model.py]        |
|                                                          |               |
|                                                          v               |
|                                                     (model.pkl)          |
+--------------------------------------------------------------------------+
                                                           |
                                                           | Loads on startup
                                                           v
+--------------------------------------------------------------------------+
|                             2. ONLINE INFERENCE                          |
|                                                                          |
|  [Frontend (UI)]   ---(POST /recommend: "Laptop")--->   [Flask Backend]  |
|         ^                                                     |          |
|         |                                                     | Filters  |
|         |                                                     v & Sorts  |
|         +-------------(Sorted Recommendations)------------- [recommend.py]|
+--------------------------------------------------------------------------+
```

---

## 📂 Folder Structure

```
smartcart-ai/
├── backend/
│   ├── generate_data.py   # Synthesizes 500 transaction samples with conditional bundling
│   ├── train_model.py     # Generates association rules and exports to model.pkl
│   ├── recommend.py       # Reusable recommendation lookup, scoring & sorting logic
│   ├── app.py             # Flask server with REST API & CORS enabled
│   ├── requirements.txt   # Python package dependencies
│   ├── model.pkl          # Trained model storing association rules (generated)
│   └── transactions.csv   # Historical market basket transactions dataset (generated)
│
├── frontend/
│   ├── index.html         # Responsive, SEO-optimized web application interface
│   ├── style.css          # Premium modern CSS variables (Light/Dark themes, glassmorphism)
│   └── script.js          # Vanilla JS interface handler and endpoint client
│
├── vercel.json            # Vercel Serverless routing config
├── README.md              # Project documentation
└── .gitignore             # Git ignored files
```

---

## 🛠️ Tech Stack

*   **Machine Learning**: `mlxtend` (Apriori & Association Rules), `pandas`
*   **Backend Server**: `Flask` (Python 3), `flask-cors`
*   **Frontend UI**: HTML5, Vanilla CSS3, Vanilla JS
*   **Deployment**: `Vercel` Serverless Functions & Static Web Hosting

---

## ⚡ Installation & Local Setup

### 1. Python Environment Setup
Navigate to the root directory and create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate
```

### 2. Dependency Installation
Install all the necessary packages:

```bash
pip install -r backend/requirements.txt
```

### 3. Generate Transactions Dataset
Generate the synthetic database of 500 transactions implementing conditional probability rules (Laptop Tech Bundle, Smartphone Mobile Bundle, DSLR Photography Bundle):

```bash
python backend/generate_data.py
```
*This outputs `backend/transactions.csv`.*

### 4. Train the Apriori Model
Perform Market Basket Analysis on the transactions to build association rules:

```bash
python backend/train_model.py
```
*This outputs `backend/model.pkl`.*

### 5. Running the Backend API
Start the local Flask development server:

```bash
python backend/app.py
```
*The server will run on `http://127.0.0.1:5000`.*

### 6. Running the Frontend
You can launch the frontend directly by opening `frontend/index.html` in any browser, or serve it using a local HTTP server:

```bash
# Serve from the root folder
python -m http.server 8000
```
Open `http://localhost:8000/frontend/` in your browser. The JavaScript code is smart enough to detect local hosting and automatically connects to the Flask API at `http://127.0.0.1:5000`.

---

## 🔌 API Documentation

### 1. Health Status
Verify backend server status and model loading state.

*   **Endpoint**: `/health` or `/`
*   **Method**: `GET`
*   **Success Response** (200 OK):
    ```json
    {
      "dataset_exists": true,
      "message": "SmartCart AI API is running.",
      "model_loaded": true,
      "status": "healthy"
    }
    ```

### 2. Get Product Recommendations
Retrieve product bundle suggestions based on a item cart query.

*   **Endpoint**: `/recommend`
*   **Method**: `POST`
*   **Headers**: `Content-Type: application/json`
*   **Example Request Body**:
    ```json
    {
      "product": "Laptop"
    }
    ```
*   **Example Response Body** (200 OK):
    ```json
    {
      "product": "Laptop",
      "recommendations": [
        {
          "item": "Mouse",
          "confidence": 0.7067,
          "lift": 1.7612,
          "support": 0.212
        },
        {
          "item": "Laptop Bag",
          "confidence": 0.6333,
          "lift": 2.0107,
          "support": 0.19
        }
      ]
    }
    ```
*   **Error Responses**:
    *   **400 Bad Request** (Empty Input): `{"error": "Empty input", "message": "The product parameter is required..."}`
    *   **400 Bad Request** (Invalid Product): `{"error": "Invalid product", "message": "'Banana' is not a recognized product..."}`
    *   **500 Internal Error** (Missing Model): `{"error": "Missing model configuration", "message": "The association rules model has not been trained..."}`

---

## 📸 Interface Screenshots

| Light Mode (Default) | Dark Mode |
| --- | --- |
| ![Light Mode Layout](https://via.placeholder.com/600x400?text=Light+Mode+UI+Mockup) | ![Dark Mode Layout](https://via.placeholder.com/600x400?text=Dark+Mode+UI+Mockup) |

---

## 🚀 Deployment Guide (Vercel Serverless)

This project is pre-configured to be deployed directly to Vercel. Vercel automatically deploys the static files from the `frontend` folder and routes the Python backend through serverless functions using `vercel.json` configuration.

### Deployment Steps:
1. Install the Vercel CLI: `npm install -g vercel`
2. Run `vercel` in the project root directory.
3. Link the project to your Vercel account when prompted.
4. Deploy the production version with `vercel --prod`.

---

## 📄 Resume-Ready Project Description

**SmartCart AI — E-commerce Cross-Selling Recommendation System (ML / Full-Stack)**
*   **Core Engineering**: Designed and built an end-to-end recommendation engine mapping transaction sets with the **Apriori Algorithm** to surface cross-category items, saving pre-calculated association rules as pickled artifacts (`model.pkl`) to achieve **O(1) inference time** on API queries.
*   **Algorithms & Logic**: Analyzed multi-product transactions to extract rules meeting minimum Support ($\ge 0.05$) and Lift ($\ge 1.2$) thresholds, ranking outputs dynamically using a multi-variable sort hierarchy (Lift $\rightarrow$ Confidence $\rightarrow$ Support).
*   **API & Serverless Architecture**: Developed a Flask REST API with robust CORS configurations, modular input sanitization, and structured health diagnostic routes, fully optimized for serverless Python runtimes on Vercel.
*   **Frontend Design System**: Crafted a high-fidelity, responsive single-page application using modern HTML5, Vanilla JavaScript, and CSS variables supporting automated Light/Dark mode transitions, progress meters, and shimmer loaders.

---

## 📈 Future Improvements

1.  **Dynamic Support Filtering**: Add UI controls to let users adjust Support and Confidence thresholds on-the-fly.
2.  **Multi-Product Baskets**: Extend the recommendation logic to evaluate baskets containing multiple items (multi-item antecedents).
3.  **Real-Time Data Injection**: Incorporate a database (e.g. SQLite or MongoDB) to append transactions and trigger scheduled model retraining.

---

## ⚖️ License
This project is licensed under the MIT License. Feel free to clone, modify, and integrate into retail workflows.
