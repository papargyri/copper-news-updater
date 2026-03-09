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
    
    # 1. Get Article Counts
    md_df = get_historical_markdown_data()
    json_df = get_live_json_data()
    
    # Combine counts (JSON takes precedence if duplicate date)
    if not json_df.empty:
        json_counts = json_df[['Date', 'Article_Count']]
        combined_counts = pd.concat([md_df, json_counts]).drop_duplicates(subset=['Date'], keep='last')
    else:
        combined_counts = md_df
        
    combined_counts['Date'] = pd.to_datetime(combined_counts['Date'])

    # 2. Get Historical Prices (to backfill before JSON tracking started)
    if combined_counts.empty:
        print("No article data found. Cannot generate chart.")
        return
        
    min_date = combined_counts['Date'].min() - pd.Timedelta(days=14)
    max_date = datetime.now() + pd.Timedelta(days=1)
    
    copper = yf.Ticker("HG=F")
    price_data = copper.history(start=min_date.strftime('%Y-%m-%d'), end=max_date.strftime('%Y-%m-%d'))
    price_data.reset_index(inplace=True)
    price_data['Date'] = pd.to_datetime(price_data['Date'].dt.tz_localize(None).dt.strftime('%Y-%m-%d'))
    price_df = price_data[['Date', 'Close']].rename(columns={'Close': 'Copper_Price_USD'})

    # 3. Merge Data
    df = pd.merge(price_df, combined_counts, on='Date', how='left')
    df['Article_Count'] = df['Article_Count'].fillna(0)
    
    # 4. Generate Plotly Chart
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add Article Volume Bar Chart (Secondary Y-Axis)
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Article_Count'],
            name="News Article Volume",
            marker_color='rgba(158, 202, 225, 0.6)', # Soft blue, transparent
            hovertemplate="<b>Date:</b> %{x}<br><b>Articles:</b> %{y}<extra></extra>"
        ),
        secondary_y=True,
    )

    # Add Copper Price Line Chart (Primary Y-Axis)
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Copper_Price_USD'],
            name="Copper Price (HG=F)",
            mode='lines+markers',
            line=dict(color='rgba(255, 127, 14, 1)', width=3), # Orange
            marker=dict(size=4),
            hovertemplate="<b>Date:</b> %{x}<br><b>Price:</b> $%{y:.4f}<extra></extra>"
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
            rangeslider=dict(visible=True), # Adds a mini navigator map at the bottom
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
        )
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
