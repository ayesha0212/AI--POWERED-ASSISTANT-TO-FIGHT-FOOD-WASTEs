import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import os
import numpy as np
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Food Waste Reduction System",
    layout="wide"
)

# ---------------- DARK THEME ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

h1,h2,h3 {
    color:#00C853;
}

div.stButton > button {
    background-color:#00C853;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
"""
<h1 style='text-align:center;color:#00C853;'>
AI Food Waste Reduction System
</h1>
""",
unsafe_allow_html=True
)

# ---------------- DATABASE ----------------

conn = sqlite3.connect("food_ai.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password BLOB
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS donations(
user TEXT,
food TEXT,
quantity INTEGER,
expiry INTEGER
)
""")

conn.commit()

# ---------------- CACHE FUNCTIONS ----------------

@st.cache_data
def load_recipes():
    return pd.read_csv("recipes_dataset.csv")

@st.cache_data
def load_ngos():
    return pd.read_csv("ngo_locations.csv")

@st.cache_data
def load_donations():
    return pd.read_sql_query("SELECT * FROM donations", conn)

# ---------------- DATASETS ----------------

if not os.path.exists("recipes_dataset.csv"):

    df = pd.DataFrame({

        "ingredients":[
            "rice;vegetables",
            "bread;milk",
            "banana;milk",
            "potato;vegetables",
            "rice;egg"
        ],

        "recipe":[
            "Vegetable Fried Rice: Heat oil → Add vegetables → Add cooked rice → Stir fry",
            "Bread Pudding: Mix bread and milk → Add sugar → Bake",
            "Banana Smoothie: Blend banana and milk → Add honey",
            "Potato Curry: Boil potatoes → Add spices and vegetables",
            "Egg Fried Rice: Fry egg → Add cooked rice → Add soy sauce"
        ],

        "agriculture_use":[
            "Vegetable peels can be composted to enrich soil",
            "Bread crumbs can be fed to poultry",
            "Banana peels are good compost material",
            "Potato peels improve compost quality",
            "Egg shells are useful for soil calcium"
        ],

        "safety_tip":[
            "Store in fridge and eat within 24 hours",
            "Refrigerate and consume within 1 day",
            "Use ripe bananas",
            "Store in fridge and use within 24 hours",
            "Consume within 24 hours"
        ]

    })

    df.to_csv("recipes_dataset.csv", index=False)

if not os.path.exists("ngo_locations.csv"):

    df = pd.DataFrame({
        "name":["Food Bank","Helping Hands","City Shelter"],
        "lat":[12.9716,12.2958,13.0827],
        "lon":[77.5946,76.6394,80.2707]
    })

    df.to_csv("ngo_locations.csv", index=False)

# ---------------- PASSWORD FUNCTIONS ----------------

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# ---------------- FOOD RECOGNITION ----------------

def classify_food(image):

    image = image.resize((128,128))
    arr = np.array(image)

    # calculate average colors
    r = arr[:,:,0].mean()
    g = arr[:,:,1].mean()
    b = arr[:,:,2].mean()

    # simple color logic
    if g > r and g > b:
        return "vegetable"
    elif r > g and r > b:
        return "fruit"
    elif r < 100 and g < 100 and b < 100:
        return "bread"
    elif r > 200 and g > 200:
        return "rice"
    else:
        return "pasta"

# ---------------- EXPIRY PREDICTION ----------------

def predict_expiry(food):

    data = {
        "rice":12,
        "bread":6,
        "vegetable":8,
        "fruit":10,
        "pasta":24
    }

    return data.get(food,12)

# ---------------- WASTE SCORE ----------------

def calculate_score(quantity, expiry):

    score = 100

    if quantity > 10:
        score -= 20

    if expiry < 5:
        score -= 30

    if expiry < 2:
        score -= 50

    return max(score,0)

# ---------------- SESSION ----------------

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- SIDEBAR ----------------

st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
"Menu",
[
"Login/Register",
"Food Recognition",
"Donate Food",
"Recipe Generator",
"NGO Map",
"Dashboard"
]
)

# logout
if st.session_state.user:

    st.sidebar.success(f"Logged in as {st.session_state.user}")

    if st.sidebar.button("Logout"):

        st.session_state.user = None
        st.rerun()

# ---------------- LOGIN ----------------

if menu == "Login/Register":

    st.title("User Authentication")

    tab1,tab2 = st.tabs(["Login","Register"])

    with tab1:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            c.execute("SELECT * FROM users WHERE username=?",(username,))
            data = c.fetchone()

            if data and check_password(password,data[1]):

                st.session_state.user = username
                st.success("Login Successful")

            else:
                st.error("Invalid Credentials")

    with tab2:

        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")

        if st.button("Register"):

            hashed = hash_password(password)

            c.execute(
            "INSERT INTO users VALUES (?,?)",
            (username,hashed)
            )

            conn.commit()

            st.success("User Registered")

# ---------------- FOOD RECOGNITION ----------------

elif menu == "Food Recognition":

    st.title("Food Image Recognition")

    img = st.file_uploader("Upload Food Image", type=["jpg","png","jpeg"])

    if img is not None:

        image = Image.open(img)

        st.image(image,width=300)

        food = classify_food(image)

        st.success(f"Detected Food: {food}")

        expiry = predict_expiry(food)

        st.info(f"Estimated Expiry: {expiry} hours")

# ---------------- DONATE FOOD ----------------

elif menu == "Donate Food":

    if st.session_state.user is None:
        st.warning("Please login first")
        st.stop()

    st.title("Donate Food")

    food = st.text_input("Food Name")
    quantity = st.slider("Quantity",1,20)
    expiry = st.slider("Expiry Hours",1,24)

    if st.button("Calculate Waste Score"):

        score = calculate_score(quantity,expiry)

        st.metric("Waste Reduction Score",score)

        if score > 80:
            st.success("Low Waste Risk")

        elif score > 50:
            st.warning("Medium Waste Risk")

        else:
            st.error("High Waste Risk")

    if st.button("Donate Food"):

        c.execute(
        "INSERT INTO donations VALUES (?,?,?,?)",
        (st.session_state.user,food,quantity,expiry)
        )

        conn.commit()

        st.success("Food Donated")

# ---------------- RECIPE GENERATOR ----------------

elif menu == "Recipe Generator":

    st.title("Recipe Recommendation")

    ingredient = st.text_input("Enter Ingredient")

    df = load_recipes()

    if st.button("Search"):

        result = df[df["ingredients"].str.contains(
        ingredient,
        case=False,
        na=False
        )]

        if len(result)==0:

            st.warning("No recipes found")

        else:

            for i,row in result.iterrows():

                st.subheader("Recipe")

                st.write("Ingredients:",row["ingredients"])

                st.success(row["recipe"])

                st.info("Agriculture Use")
                st.write(row["agriculture_use"])

                st.warning("Safety Tip")
                st.write(row["safety_tip"])

                st.markdown("---")

# ---------------- NGO MAP ----------------

elif menu == "NGO Map":

    st.title("Nearby NGOs")

    df = load_ngos()

    m = folium.Map(location=[12.97,77.59], zoom_start=6)

    for i,row in df.iterrows():

        folium.Marker(
        [row["lat"],row["lon"]],
        popup=row["name"]
        ).add_to(m)

    folium_static(m)

# ---------------- DASHBOARD ----------------

elif menu == "Dashboard":

    if st.session_state.user is None:
        st.warning("Please login first")
        st.stop()

    st.title("Food Waste Analytics")

    df = load_donations()

    col1,col2,col3 = st.columns(3)

    col1.metric("Total Donations",len(df))

    col2.metric("Total Users",
                pd.read_sql_query("SELECT * FROM users",conn).shape[0])

    if len(df)>0:
        avg = int(df["expiry"].mean())
    else:
        avg = 0

    col3.metric("Avg Expiry",avg)

    if len(df)>0:

        fig = px.bar(
        df,
        x="food",
        y="quantity",
        color="food",
        title="Most Donated Food"
        )

        st.plotly_chart(fig,use_container_width=True)

        pie = px.pie(
        df,
        names="food",
        values="quantity",
        title="Donation Distribution"
        )

        st.plotly_chart(pie,use_container_width=True)

    st.dataframe(df)