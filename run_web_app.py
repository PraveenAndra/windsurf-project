#!/usr/bin/env python3
"""
Runner script for the AI Resume Optimization Tool web application.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.web.app import app
from src.utils.env_validator import EnvValidator

def main():
    """Run the web application with environment validation."""
    print("\n=====================================")
    print("  AI Resume Optimization Tool")
    print("  Web Application")
    print("=====================================\n")
    
    # Validate environment variables
    validator = EnvValidator()
    validator.print_config_summary()
    validator.validate_or_exit(suppress_warnings=True)
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5001))  # Default to port 5001 to avoid conflicts with AirPlay on macOS
    debug = os.environ.get("DEBUG", "False").lower() in ["true", "1", "t"]
    
    # Print startup information
    print(f"\nStarting web server at http://localhost:{port}")
    print("Press Ctrl+C to stop the server\n")
    
    # Run the Flask app
    app.run(debug=debug, host="0.0.0.0", port=port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
