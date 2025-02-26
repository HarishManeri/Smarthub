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

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Login as", ["Admin", "User"])
    
    if st.button("Login"):
        user = get_user(username)
        if user and user[1] == password and user[2] == role:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = role
            st.experimental_rerun()
        else:
            st.error("Invalid username, password, or role")

def register():
    st.title("Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type='password')
    role = st.selectbox("Register as", ["Admin", "User"])
    
    if st.button("Register"):
        if get_user(username):
            st.error("Username already exists. Please choose a different username.")
        else:
            add_user(username, password, role)
            st.success("Registration successful! You can now login.")

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
    from_email = "your_email@gmail.com"
    password = "your_password"
    
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

def main():
    st.set_page_config(page_title="Farm Goods Marketplace", layout="wide", initial_sidebar_state="expanded")
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Login", "Register", "Admin Interface", "User Interface"])
    
    if choice == "Login":
        login()
    elif choice == "Register":
        register()
    elif choice == "Admin Interface" and st.session_state.role == "Admin":
        admin_interface()
    elif choice == "User Interface" and st.session_state.logged_in:
        user_interface()
    else:
        st.error("Unauthorized access")

if __name__ == "__main__":
    main()
