from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import Food, Restaurant, Favorite, Review, User
from recommender import get_recommendations_for_food, get_recommendations_by_query

views_bp = Blueprint('views', __name__)

def login_required(f):
    """
    Decorator to protect views requiring authentication.
    """
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@views_bp.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('views.dashboard'))
    return render_template('landing.html')

@views_bp.route('/dashboard')
@login_required
def dashboard():
    # Get manual location from session, default to 'Velachery'
    current_location = session.get('location', 'Velachery')
    
    # Get filters
    category_filter = request.args.get('category')
    search_query = request.args.get('search')
    
    # Base queries
    restaurants = Restaurant.query.filter(Restaurant.location.collate('NOCASE') == current_location).all()
    restaurant_ids = [r.id for r in restaurants]
    
    # Foods query filtered by location
    foods_query = Food.query
    if restaurant_ids:
        foods_query = foods_query.filter(Food.restaurant_id.in_(restaurant_ids))
    else:
        # If no restaurants in location, just fetch foods
        foods_query = Food.query
        
    if category_filter:
        foods_query = foods_query.filter(Food.category.collate('NOCASE') == category_filter)
        
    if search_query:
        # If search query, we can also query the ML recommender!
        ml_results = get_recommendations_by_query(search_query, limit=10)
        # Filter ML results by current location if possible, or display them prominently
        foods = ml_results
    else:
        foods = [f.to_dict() for f in foods_query.all()]
        
    # Get user favorites
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    fav_food_ids = [fav.food_id for fav in favs if fav.food_id]
    fav_rest_ids = [fav.restaurant_id for fav in favs if fav.restaurant_id]
    
    # Load all distinct locations for selector
    all_locations = db_distinct_locations()
    
    # List of all categories
    categories = ["Veg", "Non-Veg", "Vegan", "Dessert"]
    
    return render_template(
        'dashboard.html',
        foods=foods,
        restaurants=restaurants,
        current_location=current_location,
        all_locations=all_locations,
        categories=categories,
        active_category=category_filter,
        search_query=search_query,
        fav_food_ids=fav_food_ids,
        fav_rest_ids=fav_rest_ids
    )

@views_bp.route('/set-location')
@login_required
def set_location():
    loc = request.args.get('location')
    if loc:
        session['location'] = loc
        flash(f"Location updated to {loc}!", "success")
    return redirect(request.referrer or url_for('views.dashboard'))

@views_bp.route('/recommendations/<int:food_id>')
@login_required
def recommendations(food_id):
    food_item = Food.query.get_or_404(food_id)
    similar_foods = get_recommendations_for_food(food_id, limit=5)
    
    # Get user favorites
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    fav_food_ids = [fav.food_id for fav in favs if fav.food_id]
    
    return render_template(
        'recommendations.html',
        food=food_item.to_dict(),
        similar_foods=similar_foods,
        fav_food_ids=fav_food_ids
    )

@views_bp.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_details(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).all()
    foods = Food.query.filter_by(restaurant_id=restaurant_id).all()
    
    # Check if restaurant is user's favorite
    is_fav = Favorite.query.filter_by(user_id=session['user_id'], restaurant_id=restaurant_id).first() is not None
    
    # Check if food item is user's favorite
    favs = Favorite.query.filter_by(user_id=session['user_id']).all()
    fav_food_ids = [fav.food_id for fav in favs if fav.food_id]
    
    return render_template(
        'restaurant.html',
        restaurant=restaurant.to_dict(),
        reviews=[r.to_dict() for r in reviews],
        foods=[f.to_dict() for f in foods],
        is_fav=is_fav,
        fav_food_ids=fav_food_ids
    )

def db_distinct_locations():
    """
    Returns unique restaurant locations in database, or fallback if none.
    """
    try:
        from models import db
        results = db.session.query(Restaurant.location).distinct().all()
        locs = [r[0] for r in results if r[0]]
        if not locs:
            return ["Adyar", "T. Nagar", "Velachery", "Nungambakkam", "OMR"]
        return locs
    except Exception:
        return ["Adyar", "T. Nagar", "Velachery", "Nungambakkam", "OMR"]
