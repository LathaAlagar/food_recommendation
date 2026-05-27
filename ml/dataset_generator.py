from models import db, User, Restaurant, Food, Review, Favorite
from werkzeug.security import generate_password_hash
import random

def seed_database():
    """
    Populates the database with realistic food, restaurant, and user data.
    """
    # Check if database is already seeded
    if User.query.first() is not None:
        print("Database already seeded.")
        return

    print("Seeding database...")

    # Create Users
    admin = User(
        username="admin",
        email="admin@foodiefinds.ai",
        password_hash=generate_password_hash("admin123"),
        role="admin"
    )
    user1 = User(
        username="john_doe",
        email="john@gmail.com",
        password_hash=generate_password_hash("password123"),
        role="user"
    )
    user2 = User(
        username="chennai_foodie",
        email="foodie@yahoo.com",
        password_hash=generate_password_hash("password123"),
        role="user"
    )
    
    db.session.add_all([admin, user1, user2])
    db.session.commit()

    # Chennai Locations
    locations = ["Adyar", "T. Nagar", "Velachery", "Nungambakkam", "OMR"]

    # Create Restaurants
    restaurants_data = [
        {
            "name": "Anjappar Chettinad",
            "cuisine": "Chettinad, South Indian, Biryani",
            "location": "Adyar",
            "rating": 4.5,
            "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 25,
            "avg_price": 400.0,
            "contact": "044-24445555"
        },
        {
            "name": "Adyar Ananda Bhavan (A2B)",
            "cuisine": "South Indian Veg, Sweets",
            "location": "Velachery",
            "rating": 4.3,
            "image_url": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 20,
            "avg_price": 250.0,
            "contact": "044-22223333"
        },
        {
            "name": "Absolute Barbecues",
            "cuisine": "Barbecue, North Indian, Buffet",
            "location": "T. Nagar",
            "rating": 4.7,
            "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 40,
            "avg_price": 800.0,
            "contact": "044-48888888"
        },
        {
            "name": "Toscanini Pizzeria",
            "cuisine": "Italian, Pizza, Desserts",
            "location": "Nungambakkam",
            "rating": 4.6,
            "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 35,
            "avg_price": 600.0,
            "contact": "044-28282828"
        },
        {
            "name": "Sangeetha Veg Restaurant",
            "cuisine": "South Indian Veg, North Indian",
            "location": "OMR",
            "rating": 4.2,
            "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 15,
            "avg_price": 300.0,
            "contact": "044-24505050"
        },
        {
            "name": "Dindigul Thalappakatti",
            "cuisine": "Biryani, South Indian Non-Veg",
            "location": "Velachery",
            "rating": 4.4,
            "image_url": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 30,
            "avg_price": 450.0,
            "contact": "044-46666666"
        },
        {
            "name": "Copper Chimney",
            "cuisine": "North Indian, Kebab, Mughlai",
            "location": "Nungambakkam",
            "rating": 4.5,
            "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 30,
            "avg_price": 700.0,
            "contact": "044-28272727"
        },
        {
            "name": "The Mineral Cafe",
            "cuisine": "Continental, Healthy Foods, Salads",
            "location": "Adyar",
            "rating": 4.4,
            "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "delivery_time": 25,
            "avg_price": 500.0,
            "contact": "044-24446666"
        }
    ]

    restaurants = []
    for r_data in restaurants_data:
        restaurant = Restaurant(**r_data)
        db.session.add(restaurant)
        restaurants.append(restaurant)
    db.session.commit()

    # Foods Data mapping:
    # Chicken Biryani (Anjappar Chettinad, Thalappakatti)
    # Veg Biryani (Sangeetha, A2B)
    # Fried Rice (Anjappar, Sangeetha)
    # Pulao (Copper Chimney)
    
    foods_data = [
        # Anjappar Chettinad (Adyar) - ID will be resolved
        {
            "name": "Chicken Biryani",
            "cuisine": "Chettinad, Indian",
            "category": "Non-Veg",
            "rating": 4.7,
            "ingredients": "Chicken, Basmati Rice, Ginger-Garlic Paste, Biryani Masala, Curd, Onion, Mint",
            "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 280.0,
            "restaurant_idx": 0
        },
        {
            "name": "Chettinad Chicken Masala",
            "cuisine": "Chettinad, Indian",
            "category": "Non-Veg",
            "rating": 4.6,
            "ingredients": "Chicken, Chettinad Masala, Coconut, Tomato, Curry Leaves, Fennel, Cardamom",
            "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 240.0,
            "restaurant_idx": 0
        },
        {
            "name": "Mutton Chukka",
            "cuisine": "Chettinad, Indian",
            "category": "Non-Veg",
            "rating": 4.8,
            "ingredients": "Mutton, Small Onions, Pepper, Ginger, Garlic, Curry Leaves, Spices",
            "image_url": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 320.0,
            "restaurant_idx": 0
        },
        {
            "name": "Chicken Fried Rice",
            "cuisine": "Indo-Chinese",
            "category": "Non-Veg",
            "rating": 4.4,
            "ingredients": "Rice, Chicken, Egg, Soy Sauce, Cabbage, Carrot, Spring Onion, White Pepper",
            "image_url": "https://images.unsplash.com/photo-1603133872878-6967b68270c6?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 200.0,
            "restaurant_idx": 0
        },
        
        # Adyar Ananda Bhavan (Velachery)
        {
            "name": "Special Ghee Roast Dosa",
            "cuisine": "South Indian Veg",
            "category": "Veg",
            "rating": 4.6,
            "ingredients": "Rice Batter, Urad Dal, Ghee, Sambar, Coconut Chutney, Tomato Chutney",
            "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 120.0,
            "restaurant_idx": 1
        },
        {
            "name": "Paneer Butter Masala",
            "cuisine": "North Indian Veg",
            "category": "Veg",
            "rating": 4.5,
            "ingredients": "Paneer, Tomatoes, Cashews, Cream, Butter, Garam Masala, Kasuri Methi",
            "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 210.0,
            "restaurant_idx": 1
        },
        {
            "name": "Veg Biryani",
            "cuisine": "Indian Veg",
            "category": "Veg",
            "rating": 4.2,
            "ingredients": "Basmati Rice, Carrot, Beans, Peas, Potato, Biryani Spices, Mint, Saffron",
            "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 180.0,
            "restaurant_idx": 1
        },
        
        # Absolute Barbecues (T. Nagar)
        {
            "name": "Barbecue Grill Platter",
            "cuisine": "Barbecue, North Indian",
            "category": "Non-Veg",
            "rating": 4.8,
            "ingredients": "Chicken Wings, Fish Tikka, Prawns, Paneer Tikka, Pineapple, Barbecue Sauce, Spices",
            "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 750.0,
            "restaurant_idx": 2
        },
        
        # Toscanini Pizzeria (Nungambakkam)
        {
            "name": "Margherita Pizza",
            "cuisine": "Italian",
            "category": "Veg",
            "rating": 4.6,
            "ingredients": "Pizza Dough, Tomato Sauce, Fresh Mozzarella Cheese, Extra Virgin Olive Oil, Fresh Basil Leaves",
            "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 380.0,
            "restaurant_idx": 3
        },
        {
            "name": "Creamy Alfredo Pasta",
            "cuisine": "Italian",
            "category": "Veg",
            "rating": 4.4,
            "ingredients": "Penne Pasta, Heavy Cream, Parmesan Cheese, Garlic, Butter, Parsley, Mushrooms",
            "image_url": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 340.0,
            "restaurant_idx": 3
        },
        {
            "name": "Tiramisu",
            "cuisine": "Italian, Dessert",
            "category": "Dessert",
            "rating": 4.8,
            "ingredients": "Mascarpone Cheese, Espresso Coffee, Ladyfinger Biscuits, Cocoa Powder, Egg Yolks, Sugar",
            "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 220.0,
            "restaurant_idx": 3
        },

        # Sangeetha Veg Restaurant (OMR)
        {
            "name": "Masala Dosa",
            "cuisine": "South Indian Veg",
            "category": "Veg",
            "rating": 4.5,
            "ingredients": "Rice Batter, Potato Masala, Mustard Seeds, Curry Leaves, Onion, Turmeric, Chutney",
            "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 100.0,
            "restaurant_idx": 4
        },
        {
            "name": "Sambar Idli (2 Pcs)",
            "cuisine": "South Indian Veg",
            "category": "Veg",
            "rating": 4.4,
            "ingredients": "Rice, Urad Dal, Lentils, Ghee, Tamarind, Drumstick, Coriander Leaves, Mustard",
            "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 70.0,
            "restaurant_idx": 4
        },
        {
            "name": "Veg Fried Rice",
            "cuisine": "Indo-Chinese",
            "category": "Veg",
            "rating": 4.2,
            "ingredients": "Rice, Carrot, French Beans, Cabbage, Soy Sauce, Green Chili Sauce, Vinegar",
            "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 170.0,
            "restaurant_idx": 4
        },

        # Dindigul Thalappakatti (Velachery)
        {
            "name": "Thalappakatti Mutton Biryani",
            "cuisine": "South Indian Non-Veg, Biryani",
            "category": "Non-Veg",
            "rating": 4.8,
            "ingredients": "Seeraga Samba Rice, Mutton, Thalappakatti Secret Spices, Curd, Ghee, Coriander, Lemon",
            "image_url": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 350.0,
            "restaurant_idx": 5
        },
        {
            "name": "Thalappakatti Chicken Biryani",
            "cuisine": "South Indian Non-Veg, Biryani",
            "category": "Non-Veg",
            "rating": 4.6,
            "ingredients": "Seeraga Samba Rice, Chicken, Thalappakatti Secret Spices, Curd, Ghee, Mint, Green Chilies",
            "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 290.0,
            "restaurant_idx": 5
        },

        # Copper Chimney (Nungambakkam)
        {
            "name": "Chicken Tikka Masala",
            "cuisine": "North Indian, Mughlai",
            "category": "Non-Veg",
            "rating": 4.7,
            "ingredients": "Boneless Chicken, Yogurt, Kashmiri Chili, Ginger, Tomatoes, Fresh Cream, Butter, Spices",
            "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 360.0,
            "restaurant_idx": 6
        },
        {
            "name": "Mutton Pulao",
            "cuisine": "North Indian, Mughlai",
            "category": "Non-Veg",
            "rating": 4.5,
            "ingredients": "Basmati Rice, Mutton Stock, Mutton Pieces, Cloves, Cardamom, Cinnamon, Fried Onion",
            "image_url": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 340.0,
            "restaurant_idx": 6
        },
        {
            "name": "Butter Naan",
            "cuisine": "North Indian",
            "category": "Veg",
            "rating": 4.6,
            "ingredients": "Refined Flour, Yeast, Milk, Sugar, Butter, Kalonji Seeds",
            "image_url": "https://images.unsplash.com/photo-1601050690597-df056fb4ce78?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 60.0,
            "restaurant_idx": 6
        },

        # The Mineral Cafe (Adyar)
        {
            "name": "Quinoa Avocado Salad",
            "cuisine": "Healthy, Continental",
            "category": "Vegan",
            "rating": 4.5,
            "ingredients": "Quinoa, Avocado, Cherry Tomatoes, Cucumber, Olive Oil, Lemon Vinaigrette, Parsley",
            "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 290.0,
            "restaurant_idx": 7
        },
        {
            "name": "Vegan Tofu Wrap",
            "cuisine": "Healthy, Continental",
            "category": "Vegan",
            "rating": 4.3,
            "ingredients": "Whole Wheat Tortilla, Grilled Tofu, Hummus, Spinach, Carrot, Bell Pepper, Tahini",
            "image_url": "https://images.unsplash.com/photo-1626700051175-6518c4793f4f?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3",
            "price": 240.0,
            "restaurant_idx": 7
        }
    ]

    for f_data in foods_data:
        restaurant = restaurants[f_data["restaurant_idx"]]
        food = Food(
            name=f_data["name"],
            cuisine=f_data["cuisine"],
            category=f_data["category"],
            rating=f_data["rating"],
            ingredients=f_data["ingredients"],
            image_url=f_data["image_url"],
            price=f_data["price"],
            restaurant=restaurant
        )
        db.session.add(food)
        
    db.session.commit()

    # Create reviews
    # Get user john_doe
    jdoe = User.query.filter_by(username="john_doe").first()
    review1 = Review(
        user=jdoe,
        restaurant=restaurants[0],
        rating=5.0,
        comment="Best Chicken Biryani in Adyar! The Chettinad flavor is spot on."
    )
    review2 = Review(
        user=jdoe,
        restaurant=restaurants[1],
        rating=4.0,
        comment="Consistent taste and very clean place. Sambar is great."
    )
    db.session.add_all([review1, review2])
    db.session.commit()

    print("Database seeding completed successfully!")
