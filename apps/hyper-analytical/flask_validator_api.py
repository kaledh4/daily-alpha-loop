"""
Flask API for Crypto Validator
==============================

This module provides a Flask API endpoint for the CryptoValidator class,
allowing secure handling of historical price data via POST request.

Features:
- Flask REST API endpoint
- Secure JSON payload handling
- Input validation and error handling
- CORS support for web integration

Author: Hyper Analytical
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from crypto_validator import CryptoValidator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/validate_technicals', methods=['POST'])
def validate_technicals_endpoint():
    """
    Flask API endpoint for validating Bitcoin technicals.
    
    Expected JSON payload:
    {
        "historical_prices": [91000, 91500, 92000, ...],  # Array of historical prices
        "analysis_price": 95847.00,
        "analysis_sma": 88432.00,
        "analysis_ema": 89202.00,
        "live_price": 91506.00
    }
    
    Returns:
        JSON response with validation results
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['historical_prices', 'analysis_price', 'analysis_sma', 'analysis_ema', 'live_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}",
                    "status": "error"
                }), 400
        
        # Extract data
        historical_prices = pd.Series(data['historical_prices'])
        analysis_price = float(data['analysis_price'])
        analysis_sma = float(data['analysis_sma'])
        analysis_ema = float(data['analysis_ema'])
        live_price = float(data['live_price'])
        
        # Validate data types and ranges
        if len(historical_prices) < 21:
            return jsonify({
                "error": "Insufficient historical data. Minimum 21 price points required.",
                "status": "error"
            }), 400
        
        # Create validator instance
        validator = CryptoValidator(
            historical_prices=historical_prices,
            analysis_price=analysis_price,
            analysis_sma=analysis_sma,
            analysis_ema=analysis_ema
        )
        
        # Run validation
        validation_df = validator.validate_technicals(live_price)
        
        # Convert DataFrame to JSON-serializable format
        validation_results = []
        for _, row in validation_df.iterrows():
            validation_results.append({
                "metric": row['Metric'],
                "analysis_value": row['Analysis Value'],
                "calculated_value": row['Calculated Value'],
                "verdict": row['Verdict']
            })
        
        # Return results
        return jsonify({
            "status": "success",
            "results": validation_results,
            "message": "Technical validation completed successfully"
        }), 200
        
    except ValueError as ve:
        return jsonify({
            "error": f"Invalid data format: {str(ve)}",
            "status": "error"
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"Validation failed: {str(e)}",
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "Crypto Validator API",
        "version": "1.0.0"
    }), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)