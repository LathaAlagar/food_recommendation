from flask import Flask
from config import Config
from models import db
from blueprints.views import views_bp
from blueprints.auth import auth_bp
from blueprints.api import api_bp
from blueprints.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp) # url_prefix is already defined in blueprint '/admin'
    
    # Global context processor to make distinct locations available in templates if needed
    @app.context_processor
    def inject_locations():
        from blueprints.views import db_distinct_locations
        return dict(distinct_locations=db_distinct_locations())

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        from ml.dataset_generator import seed_database
        seed_database()
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
