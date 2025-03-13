import streamlit as st
import time
import random
import csv
import datetime
import pandas as pd
import plotly.express as px  # Importing Plotly
import os

# Ensure the CSV file exists
def initialize_csv():
    if not os.path.exists("typing_data.csv"):
        with open("typing_data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Date", "WPM", "Time_Taken"])

# Load text from file
def load_text():
    with open("text.txt", "r") as f:
        lines = f.readlines()
        return random.choice(lines).strip()

# Load previous typing data
def load_past_data():
    try:
        df = pd.read_csv("typing_data.csv")
        df["Date"] = pd.to_datetime(df["Date"])  # Convert Date column to datetime format
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Username", "Date", "WPM", "Time_Taken"])
    return df

# Save results to CSV (only for correct tests)
def save_results(username, wpm, time_taken):
    with open("typing_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, datetime.datetime.now(), wpm, round(time_taken, 2)])

# Streamlit UI
def main():
    initialize_csv()
    st.title("⌨️ Typing Speed Test")
    
    username = st.text_input("📝 Enter your name:")
    if not username:
        st.warning("⚠️ Please enter your name to start the test.")
        return
    
    if "test_in_progress" not in st.session_state:
        st.session_state.test_in_progress = False
    if "target_text" not in st.session_state:
        st.session_state.target_text = ""
    if "text_input" not in st.session_state:
        st.session_state.text_input = ""
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "incorrect_test" not in st.session_state:
        st.session_state.incorrect_test = False  # Flag to track incorrect test
    
    # Start Test Button
    if not st.session_state.test_in_progress:
        if st.button("🚀 Start Test"):
            st.session_state.test_in_progress = True
            st.session_state.target_text = load_text()
            st.session_state.start_time = time.time()
            st.session_state.text_input = ""
            st.session_state.incorrect_test = False  # Reset incorrect test flag
            st.rerun()
    
    if st.session_state.test_in_progress:
        st.subheader("📜 Type this:")
        st.write(f"**{st.session_state.target_text}**")  # Making text bold for better visibility
        
        # Text Input Area
        text_input = st.text_area(
            "⌨️ Start typing below:", 
            value=st.session_state.text_input,  
            height=100, 
            key="typing_area"
        )
        
        st.session_state.text_input = text_input
        
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        if text_input:
            time_elapsed = max(time.time() - st.session_state.start_time, 1)
            wpm = round((len(text_input) / 5) / (time_elapsed / 60))
            st.metric("🔥 Words Per Minute (WPM)", wpm)
            
            if text_input.strip() == st.session_state.target_text:
                st.success(f"✅ Test completed! Your WPM: {wpm}")
                save_results(username, wpm, time_elapsed)  # Save correct test

                # Reset test session
                st.session_state.test_in_progress = False
                st.session_state.start_time = None
                st.session_state.incorrect_test = False  # Reset incorrect flag

                # Next Test Button
                if st.button("🔄 Next Test"):
                    st.session_state.test_in_progress = True
                    st.session_state.target_text = load_text()
                    st.session_state.start_time = time.time()
                    st.session_state.text_input = ""
                    st.rerun()
            else:
                # Mark test as incorrect
                st.session_state.incorrect_test = True
                st.warning("⚠️ Incorrect test! The text does not match. Please proceed to the next test.")

                # Next Test Button (No saving of incorrect attempt)
                if st.button("🔄 Next Test"):
                    st.session_state.test_in_progress = True
                    st.session_state.target_text = load_text()
                    st.session_state.start_time = time.time()
                    st.session_state.text_input = ""
                    st.session_state.incorrect_test = False  # Reset flag
                    st.rerun()

    # Load and plot past results using Plotly
    df = load_past_data()
    if "Username" in df.columns:
        user_df = df[df["Username"] == username]
        if not user_df.empty:
            st.subheader("📊 Your Typing Speed Progress")
            
            # Create interactive Plotly chart
            fig = px.line(
                user_df, 
                x="Date", 
                y="WPM", 
                title="📈 Typing Speed Over Time",
                markers=True,
                template="plotly_dark",  # Dark theme for better styling
                labels={"Date": "Date", "WPM": "Words Per Minute"},
            )
            
            # Customize layout
            fig.update_traces(line=dict(width=3), marker=dict(size=8, symbol="circle"))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Words Per Minute (WPM)",
                hovermode="x unified",
                plot_bgcolor="#1E1E1E",  # Dark background for better contrast
                paper_bgcolor="#1E1E1E",
                font=dict(size=12, color="white"),
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
