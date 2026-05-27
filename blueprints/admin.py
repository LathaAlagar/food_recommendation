from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from models import db, User, Food, Restaurant
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """
    Decorator to enforce admin role.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@admin_required
def dashboard():
    users = User.query.all()
    foods = Food.query.all()
    restaurants = Restaurant.query.all()
    return render_template('admin.html', users=users, foods=foods, restaurants=restaurants)

# --- FOOD CRUD ---

@admin_bp.route('/food/add', methods=['POST'])
@admin_required
def add_food():
    name = request.form.get('name')
    cuisine = request.form.get('cuisine')
    category = request.form.get('category')
    rating = request.form.get('rating', 4.0, type=float)
    ingredients = request.form.get('ingredients')
    image_url = request.form.get('image_url')
    price = request.form.get('price', type=float)
    restaurant_id = request.form.get('restaurant_id', type=int)
    
    if not name or not price or not restaurant_id or not category:
        flash('Required fields are missing!', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    food = Food(
        name=name,
        cuisine=cuisine,
        category=category,
        rating=rating,
        ingredients=ingredients,
        image_url=image_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=60",
        price=price,
        restaurant_id=restaurant_id
    )
    db.session.add(food)
    db.session.commit()
    flash(f'Food item "{name}" added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/food/edit/<int:food_id>', methods=['POST'])
@admin_required
def edit_food(food_id):
    food = Food.query.get_or_404(food_id)
    food.name = request.form.get('name')
    food.cuisine = request.form.get('cuisine')
    food.category = request.form.get('category')
    food.rating = request.form.get('rating', 4.0, type=float)
    food.ingredients = request.form.get('ingredients')
    food.image_url = request.form.get('image_url') or food.image_url
    food.price = request.form.get('price', type=float)
    food.restaurant_id = request.form.get('restaurant_id', type=int)
    
    db.session.commit()
    flash(f'Food item "{food.name}" updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/food/delete/<int:food_id>', methods=['POST'])
@admin_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    name = food.name
    db.session.delete(food)
    db.session.commit()
    flash(f'Food item "{name}" deleted successfully!', 'info')
    return redirect(url_for('admin.dashboard'))

# --- RESTAURANT CRUD ---

@admin_bp.route('/restaurant/add', methods=['POST'])
@admin_required
def add_restaurant():
    name = request.form.get('name')
    cuisine = request.form.get('cuisine')
    location = request.form.get('location')
    rating = request.form.get('rating', 4.0, type=float)
    delivery_time = request.form.get('delivery_time', 30, type=int)
    avg_price = request.form.get('avg_price', 250.0, type=float)
    image_url = request.form.get('image_url')
    contact = request.form.get('contact')
    
    if not name or not location:
        flash('Restaurant name and location are required!', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    restaurant = Restaurant(
        name=name,
        cuisine=cuisine,
        location=location,
        rating=rating,
        delivery_time=delivery_time,
        avg_price=avg_price,
        image_url=image_url or "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&auto=format&fit=crop&q=60",
        contact=contact
    )
    db.session.add(restaurant)
    db.session.commit()
    flash(f'Restaurant "{name}" added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/restaurant/edit/<int:restaurant_id>', methods=['POST'])
@admin_required
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    restaurant.name = request.form.get('name')
    restaurant.cuisine = request.form.get('cuisine')
    restaurant.location = request.form.get('location')
    restaurant.rating = request.form.get('rating', 4.0, type=float)
    restaurant.delivery_time = request.form.get('delivery_time', 30, type=int)
    restaurant.avg_price = request.form.get('avg_price', 250.0, type=float)
    restaurant.image_url = request.form.get('image_url') or restaurant.image_url
    restaurant.contact = request.form.get('contact')
    
    db.session.commit()
    flash(f'Restaurant "{restaurant.name}" updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/restaurant/delete/<int:restaurant_id>', methods=['POST'])
@admin_required
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    name = restaurant.name
    db.session.delete(restaurant)
    db.session.commit()
    flash(f'Restaurant "{name}" deleted successfully!', 'info')
    return redirect(url_for('admin.dashboard'))

# --- USER MANAGEMENT ---

@admin_bp.route('/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot delete your own admin account!', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    name = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User account "{name}" deleted successfully!', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/toggle-admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot demote yourself!', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    user = User.query.get_or_404(user_id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f'User role for "{user.username}" updated to {user.role.upper()}!', 'success')
    return redirect(url_for('admin.dashboard'))
