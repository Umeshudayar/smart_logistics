from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
import json
from models.delivery_model import train_delivery_model, predict_delivery_time
from utils.maps_utils import get_distance_time, generate_map

app = Flask(__name__)
app.secret_key = 'smartlogistics123'  # For session management

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Initialize or load shipments data
shipments_file = 'data/shipments.csv'
if os.path.exists(shipments_file):
    shipments_df = pd.read_csv(shipments_file)
else:
    shipments_df = pd.DataFrame(columns=[
        'id', 'consignor_name', 'consignor_number', 'consignor_address',
        'consignee_name', 'consignee_number', 'consignee_address',
        'from_location', 'to_location', 'weight', 'quantity',
        'distance', 'estimated_time', 'predicted_time', 'status'
    ])
    shipments_df.to_csv(shipments_file, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/new_shipment', methods=['GET', 'POST'])
def new_shipment():
    if request.method == 'POST':
        # Extract form data
        shipment_data = {
            'id': len(shipments_df) + 1,
            'consignor_name': request.form.get('consignor_name'),
            'consignor_number': request.form.get('consignor_number'),
            'consignor_address': request.form.get('consignor_address'),
            'consignee_name': request.form.get('consignee_name'),
            'consignee_number': request.form.get('consignee_number'),
            'consignee_address': request.form.get('consignee_address'),
            'from_location': request.form.get('from_location'),
            'to_location': request.form.get('to_location'),
            'weight': float(request.form.get('weight')),
            'quantity': int(request.form.get('quantity')),
            'status': 'Pending'
        }
        
        # Calculate distance and time using Google Maps API
        pickup = shipment_data['from_location']
        delivery = shipment_data['to_location']
        
        try:
            distance, duration, polyline = get_distance_time(pickup, delivery)
            shipment_data['distance'] = distance
            shipment_data['estimated_time'] = duration
            
            # Predict delivery time using ML model
            model = train_delivery_model()
            predicted_time = predict_delivery_time(model, distance)
            shipment_data['predicted_time'] = predicted_time
            
            # Generate map visualization
            map_path = f"static/maps/shipment_{shipment_data['id']}.html"
            if not os.path.exists('static/maps'):
                os.makedirs('static/maps')
            
            generate_map(pickup, delivery, polyline, f"static/maps/shipment_{shipment_data['id']}.html")
            
            # Add to dataframe
            global shipments_df
            shipments_df = pd.concat([shipments_df, pd.DataFrame([shipment_data])], ignore_index=True)
            shipments_df.to_csv(shipments_file, index=False)
            
            return redirect(url_for('results', shipment_id=shipment_data['id']))
        
        except Exception as e:
            flash(f"Error processing shipment: {str(e)}")
            return render_template('new_shipment.html')
    
    return render_template('new_shipment.html')

@app.route('/track_shipment', methods=['GET', 'POST'])
def track_shipment():
    if request.method == 'POST':
        shipment_id = int(request.form.get('shipment_id'))
        return redirect(url_for('results', shipment_id=shipment_id))
    
    return render_template('track_shipment.html')

@app.route('/results/<int:shipment_id>')
def results(shipment_id):
    shipment = shipments_df[shipments_df['id'] == shipment_id]
    
    if not shipment.empty:
        shipment_data = shipment.iloc[0].to_dict()
        map_file = f"maps/shipment_{shipment_id}.html"
        
        return render_template('results.html', 
                              shipment=shipment_data, 
                              map_file=map_file)
    else:
        flash("Shipment not found!")
        return redirect(url_for('track_shipment'))

if __name__ == '__main__':
    app.run(debug=True)