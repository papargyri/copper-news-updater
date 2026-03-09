import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
import os
from datetime import datetime
import yfinance as yf

def get_historical_markdown_data():
    """Parses legacy daily article counts from copper_news_summary.md"""
    try:
        with open('copper_news_summary.md', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Article_Count'])

    pattern = re.compile(r'\s*-\s+\*Source:.*?\|\s*Date:\s*(\d{4}-\d{2}-\d{2})\s*\d{2}:\d{2}\*')
    dates = []
    for match in pattern.finditer(content):
        dates.append(match.group(1))

    static_pattern = re.compile(r'-\s+\*\*(.*?)\*\*.*?\((.*? \d{1,2}, \d{4})\)')
    for match in static_pattern.finditer(content):
        try:
            dt = datetime.strptime(match.group(2), '%b %d, %Y')
            dates.append(dt.strftime('%Y-%m-%d'))
        except ValueError:
            pass

    if not dates:
        return pd.DataFrame(columns=['Date', 'Article_Count'])

    counts = pd.Series(dates).value_counts().reset_index()
    counts.columns = ['Date', 'Article_Count']
    return counts

def get_live_json_data():
    """Parses live article counts and prices from data/articles_by_date.json"""
    try:
        with open('data/articles_by_date.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame(columns=['Date', 'Article_Count', 'Copper_Price_USD'])
    
    records = []
    for date_str, info in data.items():
        records.append({
            'Date': date_str,
            'Article_Count': len(info.get('articles', [])),
            'Copper_Price_USD': info.get('price_usd', None)
        })
    return pd.DataFrame(records)

def generate_interactive_chart():
    print("Generating interactive correlation chart...")
    
    # 1. Get Article Counts exclusively from JSON (which contains backfilled rigorous daily data)
    json_df = get_live_json_data()
    
    if json_df.empty:
        print("No article data found. Cannot generate chart.")
        return
        
    combined_counts = json_df[['Date', 'Article_Count']].copy()
    combined_counts['Date'] = pd.to_datetime(combined_counts['Date'])

    # 2. Get Historical Prices
    min_date = combined_counts['Date'].min() - pd.Timedelta(days=5)
    max_date = datetime.now() + pd.Timedelta(days=1)
    
    copper = yf.Ticker("HG=F")
    price_data = copper.history(start=min_date.strftime('%Y-%m-%d'), end=max_date.strftime('%Y-%m-%d'))
    price_data.reset_index(inplace=True)
    price_data['Date'] = pd.to_datetime(price_data['Date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d'))
    price_df = price_data[['Date', 'Close']].rename(columns={'Close': 'Copper_Price_USD'})

    # 3. Merge Data
    df = pd.merge(price_df, combined_counts, on='Date', how='left')
    df['Article_Count'] = df['Article_Count'].fillna(0)
    df['Is_Weekend'] = df['Date'].dt.dayofweek >= 5
    
    # 4. Generate Plotly Chart
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add Article Volume Line Chart (Secondary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Article_Count'],
            name="News Article Volume",
            mode='lines',
            line=dict(color='rgba(31, 119, 180, 1)', width=2), # Solid Blue
            fill='tozeroy', # Fill area under the line to make it look grounded
            fillcolor='rgba(31, 119, 180, 0.2)', # Transparent blue fill
            hovertemplate="<b>Date:</b> %{x}<br><b>Articles:</b> %{y}<extra></extra>"
        ),
        secondary_y=True,
    )

    # Add Copper Price Line Chart (Primary Y-Axis)
    # The continuous line runs through all days
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Copper_Price_USD'],
            name="Copper Price (HG=F)",
            mode='lines',
            line=dict(color='rgba(255, 127, 14, 1)', width=3), # Orange
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> $%{y:.4f}<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # Highlight weekend carryover prices with different markers overlayed on the line
    weekend_df = df[df['Is_Weekend']]
    fig.add_trace(
        go.Scatter(
            x=weekend_df['Date'],
            y=weekend_df['Copper_Price_USD'],
            name="Weekend Carryover Price",
            mode='markers',
            marker=dict(color='rgba(255, 195, 114, 1)', size=6, symbol='circle-open', line=dict(width=2)), # Lighter orange hollow circle
            hovertemplate="<b>Date:</b> %{x} (Weekend)<br><b>Carried Price:</b> $%{y:.4f}<extra></extra>"
        ),
        secondary_y=False,
    )

    # Set up Layout with Interactive Features
    fig.update_layout(
        title={
            'text': "<b>Copper Price vs. Premium News Volume</b>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        xaxis=dict(
            title="Date",
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1W", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            ),
            rangeslider=dict(visible=False), # Removed the confusing bottom minimap plot
            type="date"
        ),
        hovermode="x unified", # Shows tooltip for both charts at the exact x-axis position
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        annotations=[
            dict(
                text="<i>*Note: Weekend prices are carried over from Friday's market close as markets are closed on Saturday/Sunday.</i>",
                showarrow=False,
                xref="paper", yref="paper",
                x=0, y=-0.15, # Position below the chart
                xanchor="left", yanchor="top",
                font=dict(size=12, color="gray")
            )
        ]
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Copper Futures Price (USD)</b>", secondary_y=False, showgrid=True, gridcolor='lightgrey')
    fig.update_yaxes(title_text="<b>News Article Volume</b>", secondary_y=True, showgrid=False)

    # Save to HTML
    output_path = "copper_analysis_chart.html"
    fig.write_html(output_path)
    print(f"Chart successfully saved to {output_path}")

if __name__ == "__main__":
    generate_interactive_chart()
