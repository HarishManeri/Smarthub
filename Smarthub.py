import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state for products and users
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame(columns=['Product', 'Price', 'Available', 'Quality', 'Date of Produce', 'Shelf Life', 'Image'])

if 'users' not in st.session_state:
    st.session_state.users = pd.DataFrame(columns=['Username', 'Password', 'Role'])

# Initialize admin credentials
if 'admin' not in st.session_state:
    st.session_state.admin = {'username': 'admin', 'password': 'admin'}

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
        if product_name in st.session_state.products['Product'].values:
            st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Price'] = product_price
            st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Available'] = product_available
            st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Quality'] = product_quality
            st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Date of Produce'] = date_of_produce
            st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Shelf Life'] = shelf_life
            if product_image is not None:
                st.session_state.products.loc[st.session_state.products['Product'] == product_name, 'Image'] = product_image.read()
            st.success("Product updated successfully!")
        else:
            new_product = pd.DataFrame([[product_name, product_price, product_available, product_quality, date_of_produce, shelf_life, product_image.read() if product_image is not None else None]], 
                                        columns=st.session_state.products.columns)
            st.session_state.products = pd.concat([st.session_state.products, new_product], ignore_index=True)
            st.success("Product added successfully!")

    # Display current products
    st.write("Current Products")
    for index, row in st.session_state.products.iterrows():
        st.image(row['Image'], use_column_width=True)
        st.write(f"**Product:** {row['Product']}, **Price:** {row['Price']}, **Available:** {row['Available']}, **Quality:** {row['Quality']}, **Date of Produce:** {row['Date of Produce']}, **Shelf Life:** {row['Shelf Life']} days")

# Function to display user interface
def user_interface():
    st.title("User   Interface")
    
    st.subheader("Available Products")
    for index, row in st.session_state.products.iterrows():
        st.image(row['Image'], use_column_width=True)
        st.write(f"**Product:** {row['Product']}, **Price:** {row['Price']}, **Available:** {row['Available']}, **Quality:** {row['Quality']}, **Date of Produce:** {row['Date of Produce']}, **Shelf Life:** {row['Shelf Life']} days")
    
    selected_product = st.selectbox("Select a product", st.session_state.products['Product'])
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
            if username == st.session_state.admin['username'] and password == st.session_state.admin['password']:
                st.session_state.role = "Admin"
                st.success("Logged in as Admin")
                admin_interface()  # Redirect to admin interface
            else:
                st.error("Incorrect admin credentials")
        elif role == "User ":
            if username in st.session_state.users['Username'].values:
                user_password = st.session_state.users.loc[st.session_state.users['Username'] == username, 'Password'].values[0]
                if password == user_password:
                    st.session_state.role = "User "
                    st.success("Logged in as User")
                    user_interface()  # Redirect to user interface
                else:
                    st.error("Incorrect password")
            else:
                st.error("User  not found")

# Function for user registration
def register_user():
    st.title("User  Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Register"):
        if username in st.session_state.users['Username'].values:
            st.error("Username already exists")
        else:
            new_user = pd.DataFrame([[username, password, 'User ']], columns=['Username', 'Password', 'Role'])
            st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
            st.success("User  registered successfully!")

# Function for admin registration
def register_admin():
    st.title("Admin Registration")
    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type='password')

    if st.button("Register Admin"):
        if username == st.session_state.admin['username']:
            st.error("Admin username already exists")
        else:
            st.session_state.admin['username'] = username
            st.session_state.admin['password'] = password
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
