from flask import Blueprint, request, jsonify, session
from models import db, Food, Restaurant, Favorite, Review, ChatHistory, User
from blueprints.auth import token_required
from recommender import get_recommendations_for_food, get_recommendations_by_query, get_location_recommendations
import os
import google.generativeai as genai

api_bp = Blueprint('api', __name__)

# Configure Gemini if key is present
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Helper function to get current user from session or JWT token
def get_current_user_from_request():
    # If using API token header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        try:
            import jwt
            from flask import current_app
            data = jwt.decode(token, current_app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'])
            return User.query.get(data['sub'])
        except Exception:
            return None
    # If using Session Cookie
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@api_bp.route('/foods', methods=['GET'])
def get_foods():
    category = request.args.get('category')
    cuisine = request.args.get('cuisine')
    location = request.args.get('location')
    search = request.args.get('search')
    
    query = Food.query
    
    # If location is provided, filter foods by restaurant location
    if location:
        query = query.join(Restaurant).filter(Restaurant.location.collate('NOCASE') == location)
        
    if category:
        query = query.filter(Food.category.collate('NOCASE') == category)
        
    if cuisine:
        query = query.filter(Food.cuisine.like(f"%{cuisine}%"))
        
    if search:
        query = query.filter((Food.name.like(f"%{search}%")) | (Food.ingredients.like(f"%{search}%")))
        
    foods = query.all()
    return jsonify([f.to_dict() for f in foods])

@api_bp.route('/foods/<int:food_id>', methods=['GET'])
def get_food_details(food_id):
    food = Food.query.get_or_404(food_id)
    return jsonify(food.to_dict())

@api_bp.route('/recommendations/<int:food_id>', methods=['GET'])
def get_similar_recommendations(food_id):
    limit = request.args.get('limit', 5, type=int)
    recommendations = get_recommendations_for_food(food_id, limit=limit)
    return jsonify(recommendations)

@api_bp.route('/search', methods=['GET'])
def search_food_recommendations():
    q = request.args.get('q', '')
    limit = request.args.get('limit', 5, type=int)
    if not q:
        return jsonify([])
    recommendations = get_recommendations_by_query(q, limit=limit)
    return jsonify(recommendations)

@api_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    location = request.args.get('location')
    query = Restaurant.query
    if location:
        query = query.filter(Restaurant.location.collate('NOCASE') == location)
    restaurants = query.all()
    return jsonify([r.to_dict() for r in restaurants])

@api_bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant_details(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    reviews = Review.query.filter_by(restaurant_id=restaurant_id).order_by(Review.created_at.desc()).all()
    foods = Food.query.filter_by(restaurant_id=restaurant_id).all()
    
    res_dict = restaurant.to_dict()
    res_dict['reviews'] = [rev.to_dict() for rev in reviews]
    res_dict['menu'] = [f.to_dict() for f in foods]
    return jsonify(res_dict)

@api_bp.route('/restaurants/<int:restaurant_id>/reviews', methods=['POST'])
def add_review(restaurant_id):
    user = get_current_user_from_request()
    if not user:
        return jsonify({'message': 'Authentication required!'}), 401
        
    data = request.get_json() or {}
    rating = data.get('rating')
    comment = data.get('comment', '')
    
    if not rating:
        return jsonify({'message': 'Rating is required!'}), 400
        
    review = Review(
        user_id=user.id,
        restaurant_id=restaurant_id,
        rating=float(rating),
        comment=comment
    )
    db.session.add(review)
    
    # Update restaurant average rating
    restaurant = Restaurant.query.get(restaurant_id)
    all_reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
    total_rating = sum([r.rating for r in all_reviews]) + float(rating)
    restaurant.rating = round(total_rating / (len(all_reviews) + 1), 1)
    
    db.session.commit()
    
    return jsonify({'message': 'Review added successfully!', 'review': review.to_dict()}), 201

@api_bp.route('/favorites', methods=['GET'])
def get_favorites():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'message': 'Authentication required!'}), 401
        
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    
    fav_foods = []
    fav_restaurants = []
    
    for fav in favorites:
        if fav.food_id:
            food = Food.query.get(fav.food_id)
            if food:
                fav_foods.append(food.to_dict())
        if fav.restaurant_id:
            rest = Restaurant.query.get(fav.restaurant_id)
            if rest:
                fav_restaurants.append(rest.to_dict())
                
    return jsonify({
        'foods': fav_foods,
        'restaurants': fav_restaurants
    })

@api_bp.route('/favorites/toggle', methods=['POST'])
def toggle_favorite():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'message': 'Authentication required!'}), 401
        
    data = request.get_json() or {}
    food_id = data.get('food_id')
    restaurant_id = data.get('restaurant_id')
    
    if not food_id and not restaurant_id:
        return jsonify({'message': 'Either food_id or restaurant_id must be provided!'}), 400
        
    # Toggle Food favorite
    if food_id:
        existing = Favorite.query.filter_by(user_id=user.id, food_id=food_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'message': 'Removed from favorites', 'is_favorite': False}), 200
        else:
            new_fav = Favorite(user_id=user.id, food_id=food_id)
            db.session.add(new_fav)
            db.session.commit()
            return jsonify({'message': 'Added to favorites', 'is_favorite': True}), 201
            
    # Toggle Restaurant favorite
    if restaurant_id:
        existing = Favorite.query.filter_by(user_id=user.id, restaurant_id=restaurant_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({'message': 'Removed from favorites', 'is_favorite': False}), 200
        else:
            new_fav = Favorite(user_id=user.id, restaurant_id=restaurant_id)
            db.session.add(new_fav)
            db.session.commit()
            return jsonify({'message': 'Added to favorites', 'is_favorite': True}), 201

@api_bp.route('/chatbot/history', methods=['GET'])
def get_chat_history():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'message': 'Authentication required!'}), 401
        
    history = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.timestamp.asc()).all()
    return jsonify([h.to_dict() for h in history])

@api_bp.route('/chatbot', methods=['POST'])
def chatbot_chat():
    user = get_current_user_from_request()
    if not user:
        return jsonify({'message': 'Authentication required!'}), 401
        
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'message': 'Message is empty!'}), 400
        
    # Save User message
    user_history = ChatHistory(user_id=user.id, role='user', message=user_message)
    db.session.add(user_history)
    db.session.commit()
    
    # Retrieve past 10 conversations for context
    history_records = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.timestamp.desc()).limit(11).all()
    history_records.reverse()  # chronological order
    
    # Prepare chatbot response
    bot_message = ""
    
    # Try calling Gemini API
    if GEMINI_KEY:
        try:
            # Build conversation prompt context
            system_instruction = (
                "You are FoodieFinds AI, an elite virtual food assistant specialized in culinary recommendations. "
                "You are an expert on foods in Chennai (zones: Adyar, T. Nagar, Velachery, Nungambakkam, OMR), "
                "nearby trending dining places, budget-friendly meals, healthy diet ideas, and weather-based recommendations. "
                "Keep responses concise, lively, markdown-formatted, and user-friendly. "
                "Structure recommendations into readable bullet points or small grids. "
                "If the user asks about the current application, guide them to search on the main dashboard, "
                "filter by location manually in the header, or browse the similar foods recommendation section. "
            )
            
            # Format history for Gemini
            chat_context = []
            for h in history_records[:-1]:  # exclude the current query which we will pass as user input
                role = "user" if h.role == "user" else "model"
                chat_context.append({"role": role, "parts": [h.message]})
                
            model = genai.GenerativeModel('gemini-pro')
            chat = model.start_chat(history=chat_context)
            
            prompt = f"{system_instruction}\nUser Query: {user_message}"
            response = chat.send_message(prompt)
            bot_message = response.text
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            bot_message = None # Fallback triggers
            
    # Fallback Rules-Based smart response if API key is not configured or errors out
    if not bot_message:
        bot_message = get_smart_fallback_response(user_message)
        
    # Save Assistant response
    bot_history = ChatHistory(user_id=user.id, role='model', message=bot_message)
    db.session.add(bot_history)
    db.session.commit()
    
    return jsonify({
        'reply': bot_message,
        'history': [h.to_dict() for h in ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.timestamp.asc()).all()]
    })

def get_smart_fallback_response(message):
    msg = message.lower()
    
    # Weather based recommendations
    if any(kwd in msg for kwd in ["rain", "rainy", "monsoon", "cold", "winter", "weather"]):
        return (
            "🌧️ **Weather-based Recommendation:** On a chilly or rainy day in Chennai, nothing beats a piping hot bowl of **Thalappakatti Mutton Biryani** or crispy **Ghee Roast Dosa** with hot **Sambar** from A2B!\n\n"
            "Here are some cozy options:\n"
            "* **Masala Dosa** from Sangeetha (OMR)\n"
            "* **Chettinad Chicken Masala** from Anjappar (Adyar) with hot naans\n"
            "* **Tiramisu** from Toscanini for a sweet comforting treat."
        )
        
    if any(kwd in msg for kwd in ["hot", "sunny", "summer", "warm"]):
        return (
            "☀️ **Weather-based Recommendation:** Keep it light and refreshing in the Chennai heat! "
            "How about a crisp **Quinoa Avocado Salad** or a fresh **Vegan Tofu Wrap** from The Mineral Cafe (Adyar)? "
            "Pair it with cool buttermilk or fresh juices to beat the heat!"
        )
        
    # Famous foods in Chennai / Chennai keyword
    if "chennai" in msg or "famous" in msg or "local" in msg:
        return (
            "🍛 **Chennai Delicacies:** Chennai is a food lover's paradise! Here are some legendary spots and foods you must try:\n"
            "* **Adyar**: Authentic Chettinad Mutton Chukka at *Anjappar*\n"
            "* **Velachery**: Authentic Seeraga Samba *Thalappakatti Biryani*\n"
            "* **OMR & Velachery**: Traditional South Indian Breakfast (Idli, Vada, Ghee Roast) at *A2B* or *Sangeetha*\n"
            "* **Nungambakkam**: Elegant Italian Wood-Fired Pizzas at *Toscanini Pizzeria*"
        )
        
    # Budget meals
    if any(kwd in msg for kwd in ["budget", "cheap", "cost", "price", "pocket friendly"]):
        return (
            "🪙 **Budget Meals (Under ₹150):** Super delicious food doesn't have to break the bank!\n"
            "* **Sambar Idli (2 Pcs)** at *Sangeetha Veg* (OMR) - ₹70\n"
            "* **Special Ghee Roast Dosa** at *Adyar Ananda Bhavan (A2B)* (Velachery) - ₹120\n"
            "* **Masala Dosa** at *Sangeetha Veg* (OMR) - ₹100\n"
            "* **Butter Naan** at *Copper Chimney* (Nungambakkam) - ₹60"
        )
        
    # Healthy recommendations
    if any(kwd in msg for kwd in ["healthy", "diet", "vegan", "salad", "fit", "calories"]):
        return (
            "🥗 **Healthy and Clean Dining:** Eating smart is super easy on FoodieFinds! Check out these nourishing choices:\n"
            "* **Quinoa Avocado Salad** from *The Mineral Cafe* (Adyar) - High-fiber & healthy fats\n"
            "* **Vegan Tofu Wrap** from *The Mineral Cafe* (Adyar) - Packed with plant-based protein\n"
            "* **Sambar Idli (2 Pcs)** from *Sangeetha Veg* (OMR) - Steamed, low oil, and prebiotic"
        )
        
    # Trending
    if any(kwd in msg for kwd in ["trending", "popular", "best", "famous"]):
        return (
            "🔥 **Trending Foods and Hotspots:** Here is what foodies in Chennai are ordering right now:\n"
            "1. **Thalappakatti Mutton Biryani** (Velachery) - Rated ⭐ 4.8\n"
            "2. **Barbecue Grill Platter** at *Absolute Barbecues* (T. Nagar) - Rated ⭐ 4.8\n"
            "3. **Tiramisu** from *Toscanini Pizzeria* (Nungambakkam) - Rated ⭐ 4.8"
        )
        
    # Default fallback
    return (
        "👋 Hello there! I'm your **FoodieFinds AI Assistant**.\n\n"
        "Ask me about:\n"
        "* 🍛 Famous foods in **Chennai**\n"
        "* 🌧️ Weather-based food suggestions\n"
        "* 🥗 **Healthy** & vegan options\n"
        "* 🪙 **Budget** meals (Under ₹150)\n"
        "* 🔥 **Trending** restaurants nearby\n\n"
    )
