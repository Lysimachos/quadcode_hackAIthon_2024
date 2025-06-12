import pandas as pd
import streamlit as st
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

def _display_stock_data(stock_symbol, financial_ratios, historical_prices, capitalization, recommendations):

    # Display financial ratios
    st.write(f"## {stock_symbol} Financial Ratios")
    st.write(financial_ratios)

    # Display historical prices
    st.write("## Historical Prices")
    st.line_chart(historical_prices['Close'])

    # Display market capitalization
    st.write(f"## Market Capitalization")
    st.write(f"{capitalization:,}")

    # Display recommendations
    st.write(f"## Recommendations")
    st.write(recommendations)

if __name__ == "__main__":
    st.title('Stock Data Viewer')
    stock_symbol = st.text_input('Enter Stock Symbol', 'AAPL')

    # Replace these with actual data fetching and DataFrame construction
    financial_ratios = pd.DataFrame({
        'Ratio': ['P/E', 'P/B', 'ROE'],
        'Value': [15.23, 5.12, 0.24]
    })

    historical_prices = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2020', periods=100),
        'Close': np.random.rand(100) * 100
    }).set_index('Date')

    capitalization = 2000000000000  # Example market capitalization

    recommendations = pd.DataFrame({
        'Date': pd.date_range(start='1/1/2020', periods=5),
        'Firm': ['Firm A', 'Firm B', 'Firm C', 'Firm D', 'Firm E'],
        'To Grade': ['Buy', 'Hold', 'Sell', 'Buy', 'Hold']
    })

    if st.button('Get Data'):
        _display_stock_data(stock_symbol, financial_ratios, historical_prices, capitalization, recommendations)