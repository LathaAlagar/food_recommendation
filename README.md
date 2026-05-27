#  FoodieFinds – AI Powered Food & Restaurant Recommendation System


##  Overview

FoodieFinds is a full-stack web application developed to help users discover restaurants and food items based on their preferences. The system uses Machine Learning techniques to provide personalized food recommendations and improve user experience.

The application allows users to:

* Search restaurants
* Explore cuisines
* Save favorite foods/restaurants
* Receive AI-based food suggestions



#  Features

* User Registration and Login
* Restaurant Search and Filtering
* Food Recommendation System
* Favorite Restaurants and Food Items
* User Reviews and Ratings
* AI-based Recommendation Support
* Secure Authentication using JWT
* Responsive Web Interface



#  Machine Learning Model Used

The project uses a **Content-Based Recommendation System**.

## 🔹 Techniques Used

* TF-IDF Vectorization
* Cosine Similarity Algorithm
* Data Preprocessing

## 🔹 Purpose

The recommendation system suggests restaurants and food items based on:

* Cuisine Type
* User Preferences
* Ratings
* Food Categories



#  Technologies Used

##  Frontend

* HTML
* CSS
* JavaScript

##  Backend

* Python
* Flask Framework

##  Database

* SQLite
* SQLAlchemy ORM

##  Libraries & APIs

* Pandas
* NumPy
* Scikit-learn
* PyJWT
* Google Gemini API
* python-dotenv


#  Installation Steps

## 1️. Clone the Repository

```bash
git clone <repository-url>
cd food
```


## 2️. Create Virtual Environment

```bash
python -m venv venv
```

## 3️. Activate Virtual Environment

###  Windows

```bash
venv\Scripts\activate
```

###  Linux / Mac

```bash
source venv/bin/activate
```

## 4️. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5️. Configure Environment Variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_api_key
```

## 6️. Run the Application

```bash
python app.py
```

#  Working Procedure

1. User registers and logs into the system.
2. User searches for restaurants or food items.
3. System retrieves data from SQLite database.
4. Recommendation engine analyzes food categories and user interests.
5. AI model suggests similar restaurants and food items.
6. Results are displayed through the web interface.

#  Dataset Description

The dataset contains:

* Restaurant Details
* Food Categories
* Cuisine Types
* Ratings and Reviews
* Location Information
* User Preferences

##  Sample Fields

* Restaurant Name
* Cuisine Type
* Rating
* Price Range
* Delivery Time
* Location
  

#  Results

* Successfully developed a food recommendation web application.
* Users can search restaurants and receive personalized recommendations.
* Recommendation system improves food discovery experience.
* Secure authentication and database management implemented successfully.


#  Future Enhancements

* Real-time Food Delivery Tracking
* Mobile Application Support
* Online Payment Integration
* Advanced Deep Learning Recommendation Models
* Chatbot Integration
* GPS-based Nearby Restaurant Suggestions
* Admin Dashboard and Analytics


#  Output

The system provides:

* Personalized restaurant recommendations
* Cuisine-based food suggestions
* Restaurant reviews and ratings
* User-friendly web interface


#  Conclusion

FoodieFinds is an intelligent food recommendation platform that combines web development and Machine Learning techniques to enhance restaurant discovery and user satisfaction.
