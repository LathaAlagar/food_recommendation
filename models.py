from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete-orphan")
    chat_histories = db.relationship('ChatHistory', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False) # e.g. "Adyar", "T. Nagar", "Velachery", "Nungambakkam", "OMR"
    rating = db.Column(db.Float, default=4.0)
    image_url = db.Column(db.String(500), nullable=True)
    delivery_time = db.Column(db.Integer, default=30) # in minutes
    avg_price = db.Column(db.Float, default=200.0) # average price for two
    contact = db.Column(db.String(20), nullable=True)
    
    # Relationships
    foods = db.relationship('Food', backref='restaurant', lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship('Review', backref='restaurant', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='restaurant', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cuisine': self.cuisine,
            'location': self.location,
            'rating': self.rating,
            'image_url': self.image_url,
            'delivery_time': self.delivery_time,
            'avg_price': self.avg_price,
            'contact': self.contact
        }


class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False) # "Veg", "Non-Veg", "Vegan", "Dessert"
    rating = db.Column(db.Float, default=4.0)
    ingredients = db.Column(db.Text, nullable=False) # comma-separated values
    image_url = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    
    # Relationships
    favorites = db.relationship('Favorite', backref='food', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cuisine': self.cuisine,
            'category': self.category,
            'rating': self.rating,
            'ingredients': [i.strip() for i in self.ingredients.split(',')] if self.ingredients else [],
            'image_url': self.image_url,
            'price': self.price,
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant.name if self.restaurant else "Unknown"
        }


class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'food_id': self.food_id,
            'restaurant_id': self.restaurant_id
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else "Anonymous",
            'restaurant_id': self.restaurant_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }


class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user' or 'model' / 'assistant'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }
