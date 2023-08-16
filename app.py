import pickle
import streamlit as st
import pandas as pd
import pyrebase
import ast
from geopy.geocoders import Nominatim
import time
import hashlib


firebaseConfig = {
    'apiKey': "AIzaSyAhoCOUrmxz0mV8Yc1f68T9l6vC4rDfoHc",
    'authDomain': "flipkartgrid-ea07f.firebaseapp.com",
    'projectId': "flipkartgrid-ea07f",
    'databaseURL': "https://flipkartgrid-ea07f-default-rtdb.firebaseio.com/",
    'storageBucket': "flipkartgrid-ea07f.appspot.com",
    'messagingSenderId': "750002770398",
    'appId': "1:750002770398:web:a0250bd2193ed9a8170d4f",
    'measurementId': "G-0CCGFVSCE3"
}
st.set_page_config(initial_sidebar_state="expanded")



firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

st.sidebar.title("Our App")

choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])
email = st.sidebar.text_input("email address")
password = st.sidebar.text_input('please enter your password', type='password')
login_successful = False
recommendations = []

def initialize_session_state():
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'sig' not in st.session_state:
        st.session_state.sig = None

def logout():
    st.session_state.login_successful = False
    st.title("Logged Out")
    st.info("You have been logged out. Please log in again to access the app.")

if 'login_successful' not in st.session_state:
    st.session_state.login_successful = False


if choice == 'Sign up':
    handle = st.sidebar.text_input('please enter your username', value='Default')
    user_location = st.sidebar.text_input("Enter your location")



    submit = st.sidebar.button('create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)

        if user_location:
            geolocator = Nominatim(user_agent="my_geocoder")
            location = geolocator.geocode(user_location)

            if location:
                st.write("Latitude:", location.latitude)
                st.write("Longitude:", location.longitude)

                # Write latitude and longitude to Firebase database
                location_data = {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
                db.child(user['localId']).child("user_locations").push(location_data)

                st.success("Location data written to Firebase.")
            else:
                st.warning("Location not found.")
        else:
            st.warning("Please enter your location.")

        auth.send_email_verification(user['idToken'])  # Send verification email
        st.success('Check your inbox for authorization email')
        st.balloons()
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome ' + handle)
        st.info('Login via login dropdown')

if choice == 'Login':
    col1, col2 = st.sidebar.columns(2)

    # Login button
    login = col1.button('Login')

    # Logout button
    logout_button = col2.button("Logout")
    if logout_button:
        logout()
    if login:
        user = auth.sign_in_with_email_and_password(email, password)

        time.sleep(2)

        user_info = auth.get_account_info(user['idToken'])
        if user_info.get("users", [])[0].get("emailVerified", False):
            st.session_state.login_successful = True
            st.session_state.user = user
            #can set cookies here using streamlit auth
        else:
            st.warning("Please verify your email before logging in.")

if st.session_state.login_successful:

    st.sidebar.text("Login Successful!!")

    # Load the pickled DataFrame
    with open('dataset.pkl', 'rb') as f:
        df = pickle.load(f)
    with open('sig.pkl', 'rb') as file:
        sig = pickle.load(file)

    st.session_state.df = df
    st.session_state.sig = sig

    indices = pd.Series(st.session_state.df.index, index=st.session_state.df['product_url']).drop_duplicates()


    def product_recommendation(title, sig=st.session_state.sig, indices=indices, dataset=st.session_state.df):
        indx = indices[title]

        # Get user-specific tags from cart, wishlist, and searches
        user_cart_tags = []
        user_wishlist_tags = []
        user_search_tags = []

        # Retrieve user's cart, wishlist, and search data from Firebase
        user_cart_data = db.child(st.session_state.user['localId']).child("user_cart").get().val()
        user_wishlist_data = db.child(st.session_state.user['localId']).child("user_wishlist").get().val()
        user_search_data = db.child(st.session_state.user['localId']).child("user_searches").get().val()

        if user_cart_data:
            user_cart_tags = [item['cart_tags'] for item in user_cart_data.values()]

        if user_wishlist_data:
            user_wishlist_tags = [item['wishlist_tags'] for item in user_wishlist_data.values()]

        if user_search_data:
            user_search_tags = [item.get('search_tags', []) for item in user_search_data.values()]



        # Combine user-specific tags with product tags
        user_specific_tags = 4 * user_cart_tags + 2 * user_wishlist_tags + user_search_tags
        user_specific_tags = [tag for tags in user_specific_tags for tag in tags]



        sig_scores = list(enumerate(sig[indx]))

        # Consider user-specific tags for recommendations
        for i, (tag, score) in enumerate(sig_scores):
            if tag in user_specific_tags:
                st.write(f"Adjusting score for tag {tag}")
                sig_scores[i] = (tag, score * 1.5)  # Adjust the score based on user interest

        # Sorting products
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)

        sig_scores = sig_scores[1:11]

        product_indices = [i[0] for i in sig_scores]

        return dataset['product_url'].iloc[product_indices]




    def get_product_pid(product_url):
        product_row = st.session_state.df[st.session_state.df['product_url'] == product_url]
        if not product_row.empty:
            return product_row['pid'].values[0]
        return "Product not found"


    # ... (rest of your code)

    def get_product_image(product_url):
        product_row = st.session_state.df[st.session_state.df['product_url'] == product_url]
        if not product_row.empty:
            image_url_list_str = product_row['image'].values[0]
            try:
                image_url_list = ast.literal_eval(image_url_list_str)  # Convert string to list
                if image_url_list:
                    return image_url_list[0]
            except Exception as e:
                print(f"Error converting string to list: {e}")
        return None


    def logout():
        st.session_state.login_successful = False
        st.title("Logged Out")
        st.info("You have been logged out. Please log in again to access the app.")

    def tags_from_pid(desired_pid):
        product_row = st.session_state.df[st.session_state.df['pid'] == desired_pid]


        # Get the value in the "tags" column for the specific row
        tags = product_row['tags'].values[0]
        return tags

    def tags_from_url(url):
        product_row = st.session_state.df[st.session_state.df['product_url'] == url]
        # Get the value in the "tags" column for the specific row
        tags = product_row['tags'].values[0]
        return tags


    def stateful_button(*args, key=None, **kwargs):
        if key is None:
            raise ValueError("Must pass key")

        if key not in st.session_state:
            st.session_state[key] = False

        if st.button(*args, **kwargs):
            st.session_state[key] = not st.session_state[key]

        return st.session_state[key]




    def func():
        initialize_session_state()
        st.title('Product Recommendation App')

        product_title = st.selectbox('Select a product:', st.session_state.df['product_url'])

        selected_pid = get_product_pid(product_title)

        # Use the product's PID as the key for the Recommend button
        if stateful_button('Recommend', key=f'recommend_button_{selected_pid}'):
            if selected_pid:
                search_tags_data = tags_from_pid(selected_pid)
                search_data = {
                    "search_pid": selected_pid,
                    "search_tags": search_tags_data
                }
                db.child(st.session_state.user['localId']).child("user_searches").push(search_data)
            st.success("search data written to database")

            recommendations = product_recommendation(product_title)

            st.write("Recommended Products:")

            for x in recommendations:
                pid = get_product_pid(x)
                imageobj = get_product_image(x)


                if imageobj is not None:
                    st.image(imageobj, width=250)

                product_row = df[df['product_url'] == x].iloc[0]
                product_name = product_row['product_name']
                st.write(product_name)
                add_to_cart_key = f'add_to_cart_{pid}'  # Use a unique key for each button
                add_to_wishlist_key = f'add_to_wishlist_{pid}'  # Unique key for wishlist button

                if stateful_button(f'Add {pid} to Cart', key=add_to_cart_key):
                    cart_tags_data = tags_from_pid(pid)

                    # Check if the product is already in the cart
                    cart_data = {
                        "cart_pid": pid,
                        "cart_tags": cart_tags_data
                    }
                    existing_cart_data = db.child(st.session_state.user['localId']).child("user_cart").get().val()
                    if existing_cart_data:
                        for key, value in existing_cart_data.items():
                            if value.get("cart_pid") == pid:
                                # Update existing entry
                                db.child(st.session_state.user['localId']).child("user_cart").child(key).update(
                                    cart_data)
                                break
                        else:
                            # Add new entry if not found
                            db.child(st.session_state.user['localId']).child("user_cart").push(cart_data)

                    else:
                        # If no cart data exists, add the new entry
                        db.child(st.session_state.user['localId']).child("user_cart").push(cart_data)

                    # Remove the corresponding search data if count is greater than 1
                    search_pid = selected_pid
                    search_data = db.child(st.session_state.user['localId']).child("user_searches").get().val()
                    if search_data:
                        count = 0
                        for key, value in search_data.items():
                            if value.get("search_pid") == search_pid:
                                count += 1
                                if count > 1:
                                    db.child(st.session_state.user['localId']).child("user_searches").child(
                                        key).remove()
                                    break

                if stateful_button(f'Add {pid} to Wishlist', key=add_to_wishlist_key):
                    wishlist_tags_data = tags_from_pid(pid)

                    # Check if the product is already in the wishlist
                    wishlist_data = {
                        "wishlist_pid": pid,
                        "wishlist_tags": wishlist_tags_data
                    }
                    existing_wishlist_data = db.child(st.session_state.user['localId']).child(
                        "user_wishlist").get().val()
                    if existing_wishlist_data:
                        for key, value in existing_wishlist_data.items():
                            if value.get("wishlist_pid") == pid:
                                # Update existing entry
                                db.child(st.session_state.user['localId']).child("user_wishlist").child(key).update(
                                    wishlist_data)
                                break
                        else:
                            # Add new entry if not found
                            db.child(st.session_state.user['localId']).child("user_wishlist").push(wishlist_data)

                    else:
                        # If no wishlist data exists, add the new entry
                        db.child(st.session_state.user['localId']).child("user_wishlist").push(wishlist_data)

                    # Remove the corresponding search data if count is greater than 1
                    search_pid = selected_pid
                    search_data = db.child(st.session_state.user['localId']).child("user_searches").get().val()
                    if search_data:
                        count = 0
                        for key, value in search_data.items():
                            if value.get("search_pid") == search_pid:
                                count += 1
                                if count > 1:
                                    db.child(st.session_state.user['localId']).child("user_searches").child(
                                        key).remove()
                                    break


    if __name__ == '__main__':
        func()






