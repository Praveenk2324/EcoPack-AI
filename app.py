from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load models
class ModelLoader:
    def __init__(self, model_dir="deployment_models"):
        self.model_dir = model_dir
        self.load_models()
    
    def load_models(self):
        """Load all trained models and components"""
        try:
            # Load models
            self.co2_model = joblib.load(f"{self.model_dir}/co2_prediction_model.joblib")
            self.cost_model = joblib.load(f"{self.model_dir}/cost_prediction_model.joblib")
            
            # Load encoders
            self.co2_encoder = joblib.load(f"{self.model_dir}/co2_label_encoder.joblib")
            self.cost_encoder = joblib.load(f"{self.model_dir}/cost_label_encoder.joblib")
            
            # Load feature orders
            self.co2_feature_order = joblib.load(f"{self.model_dir}/co2_feature_order.joblib")
            self.cost_feature_order = joblib.load(f"{self.model_dir}/cost_feature_order.joblib")
            
            # Load materials database
            self.materials_df = joblib.load(f"{self.model_dir}/materials_database.joblib")
            
            # Load metadata
            self.metadata = joblib.load(f"{self.model_dir}/model_metadata.joblib")
            
            print("✅ All models loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise

# Initialize models
try:
    models = ModelLoader()
except Exception as e:
    print(f"❌ Failed to load models: {e}")
    models = None

def get_recommendations(weight_kg, volume_m3, distance_km, shipping_mode, weight_co2=0.6, weight_cost=0.4):
    """Generate packaging recommendations"""
    if models is None:
        return []
    
    try:
        input_data = pd.DataFrame({
            'Weight_kg': [weight_kg],
            'Product_Volume_m3': [volume_m3], 
            'Distance_km': [distance_km],
            'Shipping_Mode': [shipping_mode]
        })
        
        recommendations = []
        for _, material in models.materials_df.iterrows():
            test_input = input_data.copy()
            test_input['Material_Name'] = material['Material_Name']
            test_input['Category'] = material['Category']
            test_input['Material_Density'] = material['Density_kg_m3']
            test_input['Cost_per_kg'] = material['Cost_per_kg']
            test_input['CO2_Emission_kg'] = material['CO2_Emission_kg']
            test_input['Biodegradable'] = material['Biodegradable']
            
            # Encode and predict
            test_encoded = test_input.copy()
            # Manual feature engineering
            test_encoded['Shipping_Mode_Road'] = 1 if test_input['Shipping_Mode'].iloc[0] == 'Road' else 0
            test_encoded['Material_CO2_Factor'] = test_input['CO2_Emission_kg']
            
            # Remove unused category encoding if it causes issues, or keep if needed for other reasons (but seems unused)
            # test_encoded['Category'] = ... (Skipping to avoid errors)
            
            # Ensure all required features exist
            for feature in models.co2_feature_order:
                if feature not in test_encoded.columns:
                    test_encoded[feature] = 0
            
            co2_pred = models.co2_model.predict(test_encoded[models.co2_feature_order])[0]
            cost_pred = models.cost_model.predict(test_encoded[models.cost_feature_order])[0]
            combined_score = (weight_co2 * co2_pred + weight_cost * cost_pred)
            
            recommendations.append({
                'Material_Name': material['Material_Name'],
                'Category': material['Category'],
                'Predicted_CO2_kg': round(co2_pred, 3),
                'Predicted_Cost_USD': round(cost_pred, 2),
                'Biodegradable': bool(material['Biodegradable']),
                'Combined_Score': round(combined_score, 3)
            })
        
        recommendations_df = pd.DataFrame(recommendations)
        return recommendations_df.sort_values('Combined_Score').head(5).to_dict('records')
    
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise e

@app.route('/')
def home():
    """Main page with interactive form"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint for packaging recommendations"""
    try:
        if models is None:
            return jsonify({'error': 'Models not loaded. Please check server configuration.'}), 500
        
        data = request.get_json()
        
        # Validate input data
        required_fields = ['weight_kg', 'volume_m3', 'distance_km', 'shipping_mode', 'optimization']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate numeric values
        if data['weight_kg'] <= 0 or data['volume_m3'] <= 0 or data['distance_km'] <= 0:
            return jsonify({'error': 'Weight, volume, and distance must be positive values'}), 400
        
        # Set optimization weights
        if data['optimization'] == 'eco':
            weight_co2, weight_cost = 0.8, 0.2
        elif data['optimization'] == 'cost':
            weight_co2, weight_cost = 0.2, 0.8
        else:
            weight_co2, weight_cost = 0.6, 0.4
        
        recommendations = get_recommendations(
            data['weight_kg'], data['volume_m3'], data['distance_km'], 
            data['shipping_mode'], weight_co2, weight_cost
        )
        
        if not recommendations:
            return jsonify({'error': 'Unable to generate recommendations. Please check your input parameters.'}), 500
        
        return jsonify(recommendations)
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': models is not None,
        'model_version': models.metadata.get('model_version', 'unknown') if models else 'unknown'
    })

@app.route('/model-info')
def model_info():
    """Get model information and statistics"""
    if models is None:
        return jsonify({'error': 'Models not loaded'}), 500
    
    return jsonify({
        'model_version': models.metadata.get('model_version', 'unknown'),
        'training_date': models.metadata.get('training_date', 'unknown'),
        'co2_model_type': models.metadata.get('co2_model_type', 'unknown'),
        'cost_model_type': models.metadata.get('cost_model_type', 'unknown'),
        'co2_rmse': models.metadata.get('co2_rmse', 'unknown'),
        'co2_mae': models.metadata.get('co2_mae', 'unknown'),
        'cost_rmse': models.metadata.get('cost_rmse', 'unknown'),
        'cost_mae': models.metadata.get('cost_mae', 'unknown'),
        'total_materials': models.metadata.get('total_materials', 0),
        'categories': models.metadata.get('categories', [])
    })

if __name__ == '__main__':
    print("🚀 Starting Eco-Friendly Packaging Recommendation System...")
    print("📱 Access the web interface at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📊 Model info: http://localhost:5000/model-info")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
