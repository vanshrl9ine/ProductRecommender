import pickle
import streamlit as st
import pandas as pd
from pathlib  import Path
import streamlit_authenticator as stauth
import pyrebase
from datetime import datetime

firebaseConfig = {
  'apiKey': "AIzaSyAhoCOUrmxz0mV8Yc1f68T9l6vC4rDfoHc",
  'authDomain': "flipkartgrid-ea07f.firebaseapp.com",
  'projectId': "flipkartgrid-ea07f",
  'databaseURL':"https://flipkartgrid-ea07f-default-rtdb.firebaseio.com/",
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
if 'login_successful' not in st.session_state:
    st.session_state.login_successful = False

if choice == 'Sign up':
    handle = st.sidebar.text_input('please enter your username', value='Default')
    submit = st.sidebar.button('create my account')
    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user['idToken'])
        st.success('Check your inbox for authorization email')
        st.balloons()
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome ' + handle)
        st.info('Login via login dropdown')

if choice == 'Login':
    login = st.sidebar.button('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.login_successful = True

if st.session_state.login_successful:

    st.sidebar.text("Login Successful!!")

    # Load the pickled DataFrame
    with open('dataset.pkl', 'rb') as f:
        df = pickle.load(f)
    with open('sig.pkl', 'rb') as file:
        sig = pickle.load(file)



    st.session_state.df = df
    st.session_state.sig = sig
    indices = pd.Series(st.session_state.df.index, index=st.session_state.df['product_name']).drop_duplicates()


    def product_recommendation(title, sig=st.session_state.sig, indices=indices, dataset=st.session_state.df):
        indx = indices[title]

        sig_scores = list(enumerate(sig[indx]))

        # Sorting products
        sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)

        sig_scores = sig_scores[1:11]

        product_indices = [i[0] for i in sig_scores]

        return dataset['product_name'].iloc[product_indices]


    # ... (previous code remains the same)

    def func():
        st.title('Product Recommendation App')

        product_title = st.selectbox('Select a product:', st.session_state.df['product_name'])

        if st.button('Recommend'):
            recommendations = product_recommendation(product_title)
            # st.write(recommendations.tolist())
            for x in recommendations.tolist():
                st.text(x)


    if __name__ == '__main__':
        func()



