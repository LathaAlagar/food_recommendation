import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import Food, Restaurant

def build_food_corpus(foods):
    """
    Builds a tag corpus for each food item to be used for TF-IDF.
    """
    corpus = []
    for food in foods:
        # Create a detailed tagging string combining name, cuisine, category, and ingredients
        ingredients_str = food.ingredients.replace(',', ' ')
        tags = f"{food.name} {food.cuisine} {food.category} {ingredients_str}"
        corpus.append({
            'id': food.id,
            'name': food.name,
            'tags': tags.lower()
        })
    return pd.DataFrame(corpus)

def get_recommendations_for_food(food_id, limit=5):
    """
    Finds foods similar to a specific food_id.
    """
    # Fetch all foods from DB
    all_foods = Food.query.all()
    if not all_foods or len(all_foods) <= 1:
        # Fallback if there is not enough data
        return [f.to_dict() for f in all_foods if f.id != food_id][:limit]

    # Build corpus dataframe
    df = build_food_corpus(all_foods)
    
    # Check if target food exists in database
    if food_id not in df['id'].values:
        return []

    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    
    # Cosine Similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Find index of target food
    idx = df[df['id'] == food_id].index[0]
    
    # Get similarity scores for this food index
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort by similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Filter out the food itself and select the top N
    sim_scores = [item for item in sim_scores if df.iloc[item[0]]['id'] != food_id]
    top_sim_scores = sim_scores[:limit]
    
    # Get indices of recommended foods
    recommended_ids = [df.iloc[i[0]]['id'] for i in top_sim_scores]
    
    # Fetch the food objects preserving order
    recommended_foods = []
    for r_id in recommended_ids:
        food_obj = Food.query.get(int(r_id))
        if food_obj:
            recommended_foods.append(food_obj.to_dict())
            
    return recommended_foods

def get_recommendations_by_query(query_text, limit=5):
    """
    Searches for foods matching a query string using TF-IDF cosine similarity.
    """
    if not query_text or len(query_text.strip()) == 0:
        return []
        
    all_foods = Food.query.all()
    if not all_foods:
        return []
        
    df = build_food_corpus(all_foods)
    
    # TF-IDF Vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    
    # Transform query string to the same vector space
    query_vec = tfidf.transform([query_text.lower()])
    
    # Compute similarity between query and all foods
    cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Rank scores
    sim_scores = list(enumerate(cosine_sim))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Filter out items with 0 similarity if we have high-scoring ones
    # but if all are 0, return nothing.
    top_sim_scores = [item for item in sim_scores if item[1] > 0.0][:limit]
    
    # If no vector-based matches, fallback to simple string matching
    if not top_sim_scores:
        matching_foods = [
            f.to_dict() for f in all_foods
            if query_text.lower() in f.name.lower() or query_text.lower() in f.cuisine.lower()
        ]
        return matching_foods[:limit]
        
    recommended_ids = [df.iloc[i[0]]['id'] for i in top_sim_scores]
    
    recommended_foods = []
    for r_id in recommended_ids:
        food_obj = Food.query.get(int(r_id))
        if food_obj:
            recommended_foods.append(food_obj.to_dict())
            
    return recommended_foods

def get_location_recommendations(location, limit=6):
    """
    Gets recommended foods located in a specific manual location.
    """
    # Find all restaurants in that location
    restaurants = Restaurant.query.filter_by(location=location).all()
    if not restaurants:
        return []
        
    restaurant_ids = [r.id for r in restaurants]
    
    # Fetch top rated foods in these restaurants
    foods = Food.query.filter(Food.restaurant_id.in_(restaurant_ids)).order_by(Food.rating.desc()).limit(limit).all()
    return [f.to_dict() for f in foods]
