#!/usr/bin/env python3
"""
Runner script for the AI Resume Optimization Tool web application.
"""
import os
from src.web.app import app

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Run the Flask app
    app.run(debug=True, host="0.0.0.0", port=port)
