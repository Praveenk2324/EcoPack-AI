# AI-Powered Sustainable Packing Recommendation System

### 🟢 **Live Demo:** [https://ecopack-ai-ojwg.onrender.com/](https://ecopack-ai-ojwg.onrender.com/)

EcoPack-AI is a FastAPI-based backend with a Streamlit frontend that uses machine learning to recommend the most sustainable and cost-effective packaging materials for your shipments. It analyzes weight, volume, distance, and shipping mode to calculate CO2 emissions and costs, helping you make eco-friendly logistics decisions.

## 🚀 Features

* **Smart Recommendations**: Suggests packaging materials based on shipment details.
* **Optimization Modes**: Choose between "Eco-Friendly," "Cost-Effective," or a "Balanced" approach.
* **Real-time Calculations**: Estimates CO2 emissions and shipping costs instantly.
* **REST API**: Exposes endpoints for integration with other logistics systems.
* **Interactive UI**: User-friendly Streamlit web interface for generating instant recommendations.
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
    Ensure the `models/` directory contains the required trained model artifacts (e.g., `co2_model.joblib`, `cost_model.joblib`, `scaler.joblib`, `materials_db.csv`, etc.). 
    If they are missing, you can generate them by running the DVC pipeline (`dvc repro`) or the training script manually (`python -m src.train`).

## 🏃‍♂️ How to Run Locally

1.  **Start the FastAPI Backend**
    Run the API using uvicorn:
    ```bash
    uvicorn app:app
    ```

2.  **Start the Streamlit Frontend**
    In a new terminal window, start the Streamlit UI:
    ```bash
    streamlit run streamlit_app.py
    ```

3.  **Access the Application**
    * **UI**: `http://localhost:8501`
    * **API Docs (Swagger UI)**: `http://localhost:8000/docs`

## 🐳 How to Run with Docker

You can run the entire application (both the FastAPI backend and Streamlit frontend) in a single Docker container.

1.  **Build the Docker Image**
    ```bash
    docker build -t ecopack-ai .
    ```

2.  **Run the Container**
    ```bash
    docker run -p 8000:8000 -p 8501:8501 ecopack-ai
    ```

3.  **Access the Application**: Open `http://localhost:8501` in your browser.

## � API Documentation

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
    {
      "product_weight_kg": 5.5,
      "shipping_distance_km": 150.0,
      "shipping_mode": "Road",
      "optimization": "eco",
      "recommendations": [
        {
          "rank": 1,
          "material_name": "Standard Corrugated Cardboard",
          "category": "Paper",
          "predicted_co2_kg": 1.25,
          "predicted_cost_usd": 5.50,
          "biodegradable": true,
          "combined_score": 0.15
        }
      ]
    }
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

1.  **Open the Web Interface**: Go to the live demo or `http://localhost:8501` (if running locally).
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
