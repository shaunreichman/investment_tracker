#!/usr/bin/env python3
"""
Main entry point for the Flask application.
"""

from src.api import create_app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting Flask app on port 5001...")
    app.run(debug=True, host='0.0.0.0', port=5001)
