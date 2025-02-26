import streamlit as st
import pandas as pd
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('farm_goods.db', check_same_thread=False)
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

c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    product_name TEXT,
    quantity INTEGER,
    mobile TEXT,
    address TEXT,
    email TEXT,
    status TEXT DEFAULT 'Pending'
)
''')

conn.commit()

ADMIN_EMAIL = "maneriharish21@gmail.com"

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = ""

# Database Functions
def add_user(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose a different username.")

def get_user(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

def add_product(product_name, price, available, quality, date_of_produce, shelf_life, image):
    c.execute("INSERT INTO products (product_name, price, available, quality, date_of_produce, shelf_life, image) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (product_name, price, available, quality, date_of_produce, shelf_life, image))
    conn.commit()

def get_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

def add_order(username, product_name, quantity, mobile, address, email):
    c.execute("INSERT INTO orders (username, product_name, quantity, mobile, address, email) VALUES (?, ?, ?, ?, ?, ?)",
              (username, product_name, quantity, mobile, address, email))
    conn.commit()
    send_email(ADMIN_EMAIL, "New Order Received", f"User {username} has ordered {quantity} of {product_name}. Contact: {mobile}, Address: {address}, Email: {email}")
    send_email(email, "Order Confirmation", f"Thank you {username} for ordering {quantity} of {product_name}. Your order will be processed soon.")

def get_orders():
    c.execute("SELECT * FROM orders")
    return c.fetchall()

def send_email(to_email, subject, body):
    from_email = "your_email@gmail.com"  # Replace with your email
    password = "your_password"  # Replace with your email password
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_email, password)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
    except Exception as e:
        st.error(f"Error sending email: {e}")

# Admin Interface
def admin_interface():
    st.title("Admin Interface")
    st.subheader("Manage Products")
    
    product_name = st.text_input("Product Name")
    product_price = st.number_input("Product Price", min_value=0.0)
    product_available = st.number_input("Available Quantity", min_value=0)
    product_quality = st.text_input("Quality (e.g., Organic, Fresh)")
    date_of_produce = st.date_input("Date of Produce", value=datetime.today())
    shelf_life = st.number_input("Shelf Life (in days)", min_value=0)
    product_image = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
    
    if st.button("Add Product"):
        if product_name:
            image_data = product_image.read() if product_image else None
            add_product(product_name, product_price, product_available, product_quality, date_of_produce, shelf_life, image_data)
            st.success("Product added successfully!")
        else:
            st.error("Please enter a product name.")
    
    st.subheader("Orders Received")
    orders = get_orders()
    for order in orders:
        st.write(f"**User:** {order[1]}, **Product:** {order[2]}, **Quantity:** {order[3]}, **Mobile:** {order[4]}, **Address:** {order[5]}, **Email:** {order[6]}, **Status:** {order[7]}")

# User Interface
def user_interface():
    st.title("User Interface")
    st.subheader("Available Products")
    
    products = get_products()
    for row in products:
        st.image(row[6], use_column_width=True)
        st.write(f"**Product:** {row[0]}, **Price:** {row[1]}, **Available:** {row[2]}, **Quality:** {row[3]}, **Date of Produce:** {row[4]}, **Shelf Life:** {row[5]} days")
    
    selected_product = st.selectbox("Select a product", [row[0] for row in products])
    quantity = st.number_input("Quantity", min_value=1)
    mobile = st.text_input("Mobile Number")
    address = st.text_area("Delivery Address")
    email = st.text_input("Email")
    
    if st.button("Order"):
        add_order(st.session_state.username, selected_product, quantity, mobile, address, email)
        st.success(f"You have ordered {quantity} of {selected_product}.")

# Main App Logic
def main():
    st.set_page_config(page_title="Farm Goods Marketplace", layout="wide", initial_sidebar_state="expanded")
    
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Login", "User Registration", "Admin Registration", "Admin Interface", "User Interface"])
    
    if choice == "Login":
        login()
    elif choice == "User Registration":
        register_user()
    elif choice == "Admin Registration":
        register_admin()
    elif choice == "Admin Interface" and st.session_state.role == "Admin":
        admin_interface()
    elif choice == "User Interface" and st.session_state.logged_in:
        user_interface()
    else:
        st.error("Unauthorized access")

if __name__ == "__main__":
    main()
