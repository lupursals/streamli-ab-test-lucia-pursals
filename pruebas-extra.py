import streamlit as st
import pandas as pd
import random
import time
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
df = sns.load_dataset("diamonds")

# Navigation
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
    def plot_chart1(df):
        plt.figure(figsize=(8, 5))
        sns.countplot(y=df["cut"], order=df["cut"].value_counts().index)
        plt.title("Count of Diamonds by Cut")
        st.pyplot(plt)

    def plot_chart2(df):
        fig, ax = plt.subplots(figsize=(6, 6))
        df["cut"].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, ax=ax)
        ax.set_ylabel("")
        ax.set_title("Percentage of Diamonds by Cut")
        st.pyplot(fig)

    # Initialize session state for experiment tracking
    if "experiment_stage" not in st.session_state:
        st.session_state.experiment_stage = 0  # 0: Start, 1: First chart, 2: Second chart, 3: Result
        st.session_state.start_time = None
        st.session_state.response_times = []
        st.session_state.charts_order = random.sample([plot_chart1, plot_chart2], 2)

    if st.session_state.experiment_stage == 0:
        if st.button("Start Experiment"):
            st.session_state.experiment_stage = 1
            st.session_state.start_time = time.time()
            st.rerun()

    elif st.session_state.experiment_stage in [1, 2]:
        st.session_state.charts_order[st.session_state.experiment_stage - 1](df)
        if st.button("I answered your question"):
            response_time = time.time() - st.session_state.start_time
            st.session_state.response_times.append(response_time)
            st.session_state.start_time = time.time()
            if st.session_state.experiment_stage == 2:
                st.session_state.experiment_stage = 3
            else:
                st.session_state.experiment_stage = 2
            st.rerun()

    elif st.session_state.experiment_stage == 3:
        st.write("### Experiment Completed!")
        first_chart_time = st.session_state.response_times[0]
        second_chart_time = st.session_state.response_times[1]
        if first_chart_time < second_chart_time:
            best_chart = "First Chart"
        else:
            best_chart = "Second Chart"
        st.write(f"You answered {best_chart} the fastest, meaning it was the most effective for you!")
        st.write(f"Time taken for First Chart: {first_chart_time:.2f} seconds")
        st.write(f"Time taken for Second Chart: {second_chart_time:.2f} seconds")
        st.write("Thank you for participating in the experiment!")

        # Option to restart the experiment
        if st.button("Restart Experiment"):
            del st.session_state.experiment_stage
            del st.session_state.start_time
            del st.session_state.response_times
            del st.session_state.charts_order
            st.rerun()
