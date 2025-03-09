import streamlit as st
import pandas as pd
import random
import time
import seaborn as sns
import matplotlib.pyplot as plt
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -- SETTING UP GOOGLE SHEETS

# Google Sheets Authentication using Streamlit Secrets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Load credentials from Streamlit Secrets
    credentials_dict = st.secrets["gcp_service_account"]

    # Ensure it's a dictionary (if loaded incorrectly as a string)
    if isinstance(credentials_dict, str):
        credentials_dict = json.loads(credentials_dict)

    # Authenticate with Google Sheets
    CREDENTIALS = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, SCOPE)
    CLIENT = gspread.authorize(CREDENTIALS)

    # Open the Google Sheet
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1gLxt5QOmQD8iz2bbcxZDvio6n8Np1JJDgBH_Aa-IVq0/edit#gid=1602658179"
    SPREADSHEET = CLIENT.open_by_url(SHEET_URL)
    WORKSHEET = SPREADSHEET.sheet1  # Select the first worksheet

except KeyError:
    st.error("Missing `gcp_service_account` credentials in Streamlit secrets!")
    st.stop()
except gspread.exceptions.SpreadsheetNotFound:
    st.error("Google Sheet not found! Make sure it exists and is shared with your service account.")
    st.stop()

# -- LOAD DATASET 
def load_data():
    data = WORKSHEET.get_all_records()
    return pd.DataFrame(data)


# -- WEBSITE/APP SETUP AND DISPLAY

# Navigation Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Experiment"])

# Home Screen
if page == "Home":
    st.title("Individual Project: A/B Testing Experiment")
    st.subheader("Data Visualization - Lucia Pursals")
    st.write("""
        This application analyzes which chart is better for visualizing diamond cuts.  
        
        You'll answer the question **"Which diamond cut is the most common?"** using two different charts.  
        After viewing each chart, click **"I answered your question"** to record the response time.  
        The total amount of time you have taken to answer will be shown. This will help me to understand which of both charts you answered quickest.
        
        Use the sidebar to navigate to the experiment.
    """)
    st.stop()

# Experiment Screen
elif page == "Experiment":
    st.title("A/B Testing for Data Visualization")
    st.write("**Which diamond cut is the most common?**")

    # Chart functions
    def plot_chart1(df): # Bar Chart of Diamond Cuts
        df = df["cut"].value_counts().reset_index()
        df.columns = ["Cut", "Count"]

        fig, ax = plt.subplots(figsize=(7, 5))

        ax.bar(df["Cut"], df["Count"])

        ax.set_title("Count of Diamonds by Cut", fontsize=14)
        ax.set_xlabel("Diamond Cut", fontsize=12)
        ax.set_ylabel("Number of Diamonds", fontsize=12)

        plt.xticks(rotation=30)

        st.pyplot(fig)

    def plot_chart2(df): # Pie Chart of Diamond Cut 
        fig, ax = plt.subplots()
        df["cut"].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, ax=ax)

        ax.set_title("Percentage of Diamonds by Cut")
        ax.set_ylabel("") # Remove y-label for a cleaner look

        st.pyplot(fig)


    # Load data only ONCE per session. I have done this for efficiency, because if not, the website was running very slow.
    if "df" not in st.session_state:
        st.session_state.df = load_data()

    # Session state variables for the experiment
    if "chart_displayed" not in st.session_state:
        st.session_state.chart_displayed = False
        st.session_state.start_time = None
        st.session_state.time_taken = None
        st.session_state.selected_chart = None

    # Show Chart Button
    if st.button("Show Chart"):
        st.session_state.selected_chart = random.choice([plot_chart1, plot_chart2])
        st.session_state.chart_displayed = True
        st.session_state.start_time = time.time()
        st.session_state.selected_chart(st.session_state.df)  # Display chart
        st.session_state.show_answer_button = True
        st.session_state.time_taken = None

    # Show Answer Button Only If Chart is Displayed and Not Answered Yet
    if st.session_state.chart_displayed and "show_answer_button" in st.session_state and st.session_state.show_answer_button:
        if st.button("I answered your question"):
            st.session_state.time_taken = time.time() - st.session_state.start_time
            st.session_state.show_answer_button = False  # Hide the button after clicking
            st.rerun()

    # Show Time Taken
    if st.session_state.time_taken is not None:
        st.write(f"Time taken to answer: **{st.session_state.time_taken:.2f} seconds**")
