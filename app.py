import streamlit as st
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Function to load data
def get_db():
    with open('db_SR.pkl', 'rb') as f:
        db_SR = pickle.load(f)
    return db_SR['df4'], db_SR['df5']

# Function to get chart type symbols
def chart_type(df, typ):
    df = df.loc[(df['close%l'] > -5) & (df['close%h'] > -5)]
    
    conditions = {
        'hosup': (abs(df['relslope_l']) < 0.01, 'close%l'),
        'hosres': (abs(df['relslope_h']) < 0.01, 'close%h'),
        'rectangle': ((abs(df['relslope_h']) < 0.02) & (abs(df['relslope_l']) < 0.02), 'close%l'),
        'upchan': ((abs((df['relslope_h'] - df['relslope_l']) / df['relslope_l']) < 0.1) & (df['relslope_l'] > 0), 'close%l'),
        'downchan': ((abs((df['relslope_h'] - df['relslope_l']) / df['relslope_l']) < 0.1) & (df['relslope_l'] < 0), 'close%h'),
        'asctriangle': ((abs(df['relslope_h']) < 0.01) & (df['relslope_l'] > 0.03), 'close%h'),
        'desctriangle': ((abs(df['relslope_l']) < 0.01) & (df['relslope_h'] < -0.03), 'close%l'),
        'triangle': ((df['relslope_l'] > 0.03) & (df['relslope_h'] < -0.03), 'close%h'),
        'fallwedge': ((df['relslope_l'] < -0.03) & (df['relslope_h'] < -0.03) & (df['relslope_h'] < df['relslope_l']) & (abs((df['relslope_h'] - df['relslope_l']) / df['relslope_l']) > 0.6), 'close%h'),
        'risewedge': ((df['relslope_l'] > 0.03) & (df['relslope_h'] > 0.03) & (df['relslope_h'] < df['relslope_l']) & (abs((df['relslope_h'] - df['relslope_l']) / df['relslope_l']) > 0.6), 'close%l')
    }
    
    if typ in conditions:
        condition, sort_key = conditions[typ]
        X = df.loc[condition].sort_values(by=sort_key, ascending=True)['symbol'].unique()
    else:
        X = []

    return X

# Function to create and save charts
def create_chart(df4, symbol):
    chart_filename = get_chart(df4, symbol)
    return chart_filename

# Example get_chart function to generate the chart
def get_chart(df, symbol):
    df_symbol = df[df['symbol'] == symbol]
    dates = df_symbol['date']
    close_prices = df_symbol['close']
    support = df_symbol['predictedPx_l']
    resistance = df_symbol['predictedPx_h']

    plt.figure(figsize=(10, 5))
    plt.plot(dates, close_prices, label='Close Price')
    plt.plot(dates, support, label='Support', linestyle='--')
    plt.plot(dates, resistance, label='Resistance', linestyle='--')
    plt.title(f'Chart for {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart to a file
    chart_filename = f"{symbol}_chart.png"
    plt.savefig(chart_filename)
    plt.close()
    
    return chart_filename

# Load data
df4, df5 = get_db()

# Load authentication configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    'my_app',
    'auth',
    cookie_expiry_days=0
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.title(f"Welcome {name}!")
    
    pattern_types = ['hosup', 'hosres', 'rectangle', 'upchan', 'downchan', 'asctriangle', 'desctriangle', 'triangle', 'fallwedge', 'risewedge']
    selected_pattern = st.selectbox("Select Chart Pattern", pattern_types)

    if selected_pattern:
        symbols = chart_type(df5, selected_pattern)
        st.write(f"Stocks showing {selected_pattern} pattern:")
        for symbol in symbols:
            st.write(symbol)
            chart_filename = create_chart(df4, symbol)
            st.image(chart_filename)
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
