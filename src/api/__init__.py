import sys
import os
from flask import Flask
from flask_cors import CORS

# Add the project root to Python path to enable domain method imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import route blueprints
from src.api.routes import fund_bp, company_bp, health_check_bp, entity_bp, banking_bp, rate_bp

# Import middleware
from src.api.middleware import setup_error_handlers, setup_logging_middleware
from src.api.middleware.database_session import setup_database_session_middleware

def create_app(db_config=None):
    app = Flask(__name__)
    CORS(app)
    
    # Set up logging configuration
    app.config['LOGGING_LEVEL'] = 'INFO'
    
    # # Initialize event consumption system
    # try:
    #     from src.fund.events.consumption import register_all_handlers
    #     register_all_handlers()
    #     app.logger.info("Event consumption system initialized successfully")
    # except Exception as e:
    #     app.logger.warning(f"Could not initialize event consumption system: {e}")
    #     # Don't fail app startup if event system fails

    # Set up middleware
    setup_database_session_middleware(app)  # Must be first - provides database sessions
    setup_error_handlers(app)
    setup_logging_middleware(app)
    
    # Register route blueprints
    app.register_blueprint(fund_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(health_check_bp)
    app.register_blueprint(entity_bp)
    app.register_blueprint(banking_bp)
    app.register_blueprint(rate_bp)

    return app 