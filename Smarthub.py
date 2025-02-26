import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('farm_goods.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_name TEXT PRIMARY KEY,
    price REAL,
    available INTEGER,
    quality TEXT,
    date_of_produce DATE,
    shelf_life INTEGER,
    image BLOB
)
''')

conn.commit()

# Function to add a user to the database
def add_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different username.")

# Function to get user from the database
def get_user(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

# Function to add a product to the database
def add_product(product_name, price, available, quality, date_of_produce, shelf_life, image):
    c.execute("INSERT INTO products (product_name, price, available, quality, date_of_produce, shelf_life, image) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (product_name, price, available, quality, date_of_produce, shelf_life, image))
    conn.commit()

# Function to get all products from the database
def get_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

# Function to display admin interface
def admin_interface():
    st.title("Admin Interface")
    
    # Manage Products
    st.subheader("Manage Products")
    
    # Section to add new products
    st.write("Add New Product")
    product_name = st.text_input("Product Name")
    product_price = st.number_input("Product Price", min_value=0.0)
    product_available = st.number_input("Available Quantity", min_value=0)
    product_quality = st.text_input("Quality (e.g., Organic, Fresh)")
    date_of_produce = st.date_input("Date of Produce", value=datetime.today())
    shelf_life = st.number_input("Shelf Life (in days)", min_value=0)
    product_image = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])

    if st.button("Add Product"):
        if product_name:
            image_data = product_image.read() if product_image is not None else None
            add_product(product_name, product_price, product_available, product_quality, date_of_produce, shelf_life, image_data)
            st.success("Product added successfully!")
        else:
            st.error("Please enter a product name.")

    # Display current products
    st.write("Current Products")
    products = get_products()
    for row in products:
                st.image(row[6], use_column_width=True)  # Image is the 7th column
        st.write(f"**Product:** {row[0]}, **Price:** {row[1]}, **Available:** {row[2]}, **Quality:** {row[3]}, **Date of Produce:** {row[4]}, **Shelf Life:** {row[5]} days")

# Function to display user interface
def user_interface():
    st.title("User  Interface")
    
    st.subheader("Available Products")
    products = get_products()
    for row in products:
        st.image(row[6], use_column_width=True)  # Image is the 7th column
        st.write(f"**Product:** {row[0]}, **Price:** {row[1]}, **Available:** {row[2]}, **Quality:** {row[3]}, **Date of Produce:** {row[4]}, **Shelf Life:** {row[5]} days")
    
    selected_product = st.selectbox("Select a product", [row[0] for row in products])
    quantity = st.number_input("Quantity", min_value=1)

    if st.button("Order"):
        st.success(f"You have ordered {quantity} of {selected_product}.")

# Function for user authentication
def login():
    st.title("Login")
    role = st.selectbox("Login as", ["Admin", "User "])
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if role == "Admin":
            if username == "admin" and password == "admin":  # Default admin credentials
                st.session_state.role = "Admin"
                st.success("Logged in as Admin")
                admin_interface()  # Redirect to admin interface
            else:
                st.error("Incorrect admin credentials")
        elif role == "User ":
            user = get_user(username)
            if user and user[1] == password:  # Check password
                st.session_state.role = "User "
                st.success("Logged in as User")
                user_interface()  # Redirect to user interface
            else:
                st.error("User  not found or incorrect password")

# Function for user registration
def register_user():
    st.title("User  Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Register"):
        if get_user(username):
            st.error("Username already exists")
        else:
            add_user(username, password, 'User ')  # Default role is User
            st.success("User  registered successfully!")

# Function for admin registration
def register_admin():
    st.title("Admin Registration")
    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type='password')

    if st.button("Register Admin"):
        if username == "admin":
            st.error("Admin username already exists")
        else:
            add_user(username, password, 'Admin')  # Set role as Admin
            st.success("Admin registered successfully!")

# Main app logic
def main():
    # Set page configuration to hide Streamlit branding
    st.set_page_config(page_title="Farm Goods Marketplace", page_icon=None, layout="wide", initial_sidebar_state="expanded")
    
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Login", "User  Registration", "Admin Registration"])

    if choice == "Login":
        login()
    elif choice == "User  Registration":
        register_user()
    elif choice == "Admin Registration":
        register_admin()

if __name__ == "__main__":
    main()
