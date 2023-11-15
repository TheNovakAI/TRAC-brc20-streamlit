import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# API Base URL
BASE_URL = "https://open-api.unisat.io/v1/indexer/brc20/TRAC/history"

# Function to get BRC-20 transaction history with authentication
def get_brc20_history(type_filter, start_date, api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"type": type_filter, "start": 0, "limit": 100}  # Adjust limit as needed
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()['data']['detail']
        df = pd.DataFrame(data)
        df['blocktime'] = pd.to_datetime(df['blocktime'], unit='s')
        return df[df['blocktime'] >= start_date]
    else:
        return pd.DataFrame()

# Streamlit App
def main():
    st.title("BRC-20 TRAC Transaction Analysis Dashboard")

    # Fetch API key from Streamlit secrets
    api_key = st.secrets["API_KEY"]

    # Time Frame Selection
    time_frames = {'Last 3 Days': 3, 'Last 7 Days': 7, 'Last 30 Days': 30}
    selected_time_frame = st.selectbox('Select Time Frame', list(time_frames.keys()))

    # Calculate start date based on selection
    start_date = datetime.datetime.now() - datetime.timedelta(days=time_frames[selected_time_frame])

    # Fetching transaction data
    buy_transactions = get_brc20_history("buy", start_date, api_key)
    sell_transactions = get_brc20_history("sell", start_date, api_key)

    # Display raw data
    st.subheader("Raw Transaction Data")
    st.write(buy_transactions)

    # Analysis
    st.subheader("Analysis")
    if not buy_transactions.empty:
        # Buyers analysis
        top_buyers = buy_transactions.groupby('from').sum().sort_values(by='amount', ascending=False).reset_index()
        st.write("Top Buyers", top_buyers)

        # Sellers analysis
        top_sellers = sell_transactions.groupby('to').sum().sort_values(by='amount', ascending=False).reset_index()
        st.write("Top Sellers", top_sellers)

        # Visualization
        st.subheader("Buying Trends")
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=buy_transactions, x='blocktime', y='amount')
        st.pyplot(plt)

    else:
        st.write("No transactions found for the selected time frame")

if __name__ == "__main__":
    main()
