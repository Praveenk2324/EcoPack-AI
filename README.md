# AI-Powered Sustainable Packing Recommendation System

### 🟢 **Live Demo:** [https://ecopack-ai-ojwg.onrender.com/](https://ecopack-ai-ojwg.onrender.com/)

EcoPack-AI is a Flask-based application that uses machine learning to recommend the most sustainable and cost-effective packaging materials for your shipments. It analyzes weight, volume, distance, and shipping mode to calculate CO2 emissions and costs, helping you make eco-friendly logistics decisions.

## 🚀 Features

* **Smart Recommendations**: Suggests packaging materials based on shipment details.
* **Optimization Modes**: Choose between "Eco-Friendly," "Cost-Effective," or a "Balanced" approach.
* **Real-time Calculations**: Estimates CO2 emissions and shipping costs instantly.
* **REST API**: Exposes endpoints for integration with other logistics systems.
* **Health Monitoring**: Includes endpoints to check system status and model metadata.

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.8 or higher
* pip (Python package manager)

### Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/praveenk2324/ecopack-ai.git](https://github.com/praveenk2324/ecopack-ai.git)
    cd ecopack-ai
    ```

2.  **Install Dependencies**
    Install the required Python packages using `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Verify Model Files**
    Ensure the `deployment_models/` directory contains the required `.joblib` files (e.g., `co2_prediction_model.joblib`, `materials_database.joblib`, etc.). The application will fail to start if these models are missing.

## 🏃‍♂️ How to Run Locally

1.  **Start the Application**
    Run the Flask app using the following command:
    ```bash
    python app.py
    ```

2.  **Access the Application**
    Once the server starts, you will see a confirmation message. Open your web browser and navigate to:
    * **URL**: `http://localhost:5001`

## 📖 API Documentation

The application provides several endpoints for developers and external integrations.

### 1. Get Recommendations
Generates packaging recommendations based on shipment parameters.

* **Endpoint**: `/recommend`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Request Body**:
    ```json
    {
      "weight_kg": 5.5,
      "volume_m3": 0.2,
      "distance_km": 150,
      "shipping_mode": "Road",   // Options: "Air", "Road", "Rail", "Sea"
      "optimization": "eco"      // Options: "eco", "cost", "balanced"
    }
    ```
* **Success Response (200 OK)**:
    ```json
    [
      {
        "Material_Name": "Corrugated Box",
        "Category": "Paper",
        "Predicted_CO2_kg": 1.25,
        "Predicted_Cost_USD": 5.50,
        "Biodegradable": true,
        "Combined_Score": 0.85
      },
      ...
    ]
    ```

### 2. System Health Check
Verifies if the server is running and models are loaded.

* **Endpoint**: `/health`
* **Method**: `GET`
* **Response**: Returns status `healthy` and model loading status.

### 3. Model Information
Retrieves metadata about the currently loaded machine learning models.

* **Endpoint**: `/model-info`
* **Method**: `GET`
* **Response**: Returns training date, model versions, and error metrics (RMSE/MAE).

## 🖥️ How to Use the UI

1.  **Open the Web Interface**: Go to the live demo or `http://localhost:5001` (if running locally).
2.  **Enter Shipment Details**:
    * **Weight (kg)**: Enter the weight of the item to be packed.
    * **Volume (m³)**: Enter the volume of the product.
    * **Distance (km)**: Enter the shipping distance.
3.  **Select Shipping Mode**: Choose from *Air*, *Road*, *Rail*, or *Sea*.
4.  **Choose Optimization Goal**:
    * **Eco-Friendly**: Prioritizes low CO2 emissions (80% weight on CO2).
    * **Cost-Effective**: Prioritizes low cost (80% weight on Cost).
    * **Balanced**: Considers both equally (60% CO2, 40% Cost).
5.  **Get Results**: Click the "Recommend" button to view the top 5 sustainable packaging options sorted by your preference.
