from flask import Flask
from config import Config
from models import db, User, Product
from routes import main as main_blueprint
from api import api as api_blueprint
from flask_login import LoginManager
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Seed admin user and sample products if they don't exist
        if not User.query.filter_by(email='admin@example.com').first():
            seed_database(app)
    
    return app

def seed_database(app):
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    with app.app_context():
        # Create admin user
        admin = User(
            email='admin@example.com',
            password=generate_password_hash('password'),
            name='Admin',
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        
        # Create sample products with better placeholder images
        products = [
            Product(
                name='Smartphone X',
                description='Latest smartphone with advanced features',
                price=699.99,
                image_url='https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=50,
                category='Electronics'
            ),
            Product(
                name='Wireless Headphones',
                description='Noise-cancelling wireless headphones',
                price=199.99,
                image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=30,
                category='Electronics'
            ),
            Product(
                name='Laptop Pro',
                description='High-performance laptop for professionals',
                price=1299.99,
                image_url='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=20,
                category='Electronics'
            ),
            Product(
                name='Smart Watch',
                description='Fitness tracking and notifications',
                price=249.99,
                image_url='https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=40,
                category='Electronics'
            ),
            Product(
                name='Coffee Maker',
                description='Automatic coffee maker with timer',
                price=89.99,
                image_url='https://images.unsplash.com/photo-1550583724-b2692b85b150?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=25,
                category='Home'
            ),
            Product(
                name='Blender',
                description='High-speed blender for smoothies',
                price=59.99,
                image_url='https://images.unsplash.com/photo-1573521193826-58c7dc2e13e3?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=35,
                category='Home'
            ),
            Product(
                name='Running Shoes',
                description='Comfortable running shoes',
                price=79.99,
                image_url='https://images.unsplash.com/photo-1460353581641-37baddab0fa2?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=60,
                category='Sports'
            ),
            Product(
                name='Yoga Mat',
                description='Non-slip yoga mat',
                price=29.99,
                image_url='https://images.unsplash.com/photo-1571902943202-507ec2618e8f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=45,
                category='Sports'
            ),
            Product(
                name='Backpack',
                description='Durable backpack for everyday use',
                price=49.99,
                image_url='https://images.unsplash.com/photo-1553062407-98eeb64c6a62?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=55,
                category='Fashion'
            ),
            Product(
                name='Desk Lamp',
                description='Adjustable LED desk lamp',
                price=39.99,
                image_url='https://images.unsplash.com/photo-1580477667995-2b94f01c9516?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&h=500&q=80',
                stock=30,
                category='Home'
            )
        ]
        
        db.session.add_all(products)
        db.session.commit()

# Create app instance at module level
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)