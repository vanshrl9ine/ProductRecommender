#Data Preprocessing and Streamlit App
This repository contains Python code to preprocess product data, build a product recommendation system using TF-IDF vectors and a sigmoid kernel, and create a Streamlit web app for interactive product recommendations. The code is designed to help you set up a complete product recommendation system using your own dataset.

#Getting Started
Follow these steps to use the provided code for building a product recommendation system and running the Streamlit app:

#Prerequisites
Make sure you have the following prerequisites installed on your system:

Python (3.6 or higher)
Required Python libraries: pandas, numpy, nltk, scikit-learn, streamlit, pyrebase, geopy


Certainly! Here's an updated version of the README markdown that includes instructions for running the Streamlit app using the app.py script:

Product Recommendation System with Data Preprocessing and Streamlit App
This repository contains Python code to preprocess product data, build a product recommendation system using TF-IDF vectors and a sigmoid kernel, and create a Streamlit web app for interactive product recommendations. The code is designed to help you set up a complete product recommendation system using your own dataset.

Getting Started
Follow these steps to use the provided code for building a product recommendation system and running the Streamlit app:

Prerequisites
Make sure you have the following prerequisites installed on your system:

Python (3.6 or higher)
Required Python libraries: pandas, numpy, nltk, scikit-learn, streamlit, pyrebase, geopy

You can install the required libraries using the following command:
pip install pandas numpy nltk scikit-learn streamlit pyrebase geopy

#Usage
Clone the repository

Download your product dataset (CSV format) and place it in the repository directory. Follow the link to the used dataset https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-products

Open the 'GridModel.ipynb' file

Run the script to preprocess the data and build the recommendation system

Once the preprocessing is complete, the script will save the processed dataset and the recommendation matrix in pickle files ('dataset.pkl' and 'sig.pkl' respectively).

Open the 'app.py' file and ensure that you have the necessary libraries and credentials set up for Pyrebase (Firebase integration).

Run the Streamlit app using the following command:

streamlit run app.py
