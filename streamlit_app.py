import streamlit as st
import requests
import pandas as pd
import datetime

# API Base URL and Endpoint
BASE_URL = "https://open-api.unisat.io/v1/indexer/brc20/TRAC/history"

# Function to get BRC-20 transaction history with pagination and authentication
def get_brc20_history(api_key, type_filter, start_date):
    tokens = []
    start = 0
    limit = 100  # Adjust the limit as per API's max limit

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    while True:
        params = {
            "type": type_filter,
            "start": start,
            "limit": limit
        }

        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            new_data = response.json()['data']['detail']
            if not new_data:
                break  # Exit the loop if no more data is found
            tokens.extend(new_data)
            start += limit  # Update start for the next iteration
        else:
            print(f"Error occurred: {response.text}")
            break

    df = pd.DataFrame(tokens)
    df['blocktime'] = pd.to_datetime(df['blocktime'], unit='s')
    return df[df['blocktime'] >= start_date]

# Streamlit App
def main():
    st.title("BRC-20 TRAC Transaction Analysis Dashboard")

    # Fetch API key
    api_key = st.secrets["API_KEY"]

    # Time Frame Selection
    time_frames = {'Last 3 Days': 3, 'Last 7 Days': 7, 'Last 30 Days': 30}
    selected_time_frame = st.selectbox('Select Time Frame', list(time_frames.keys()))

    # Calculate start date based on selection
    start_date = datetime.datetime.now() - datetime.timedelta(days=time_frames[selected_time_frame])

    # Fetching transaction data
    buy_transactions = get_brc20_history(api_key, "buy", start_date)
    sell_transactions = get_brc20_history(api_key, "sell", start_date)

    # Displaying data
    st.subheader("Buy Transactions")
    st.write(buy_transactions)

    st.subheader("Sell Transactions")
    st.write(sell_transactions)

if __name__ == "__main__":
    main()
