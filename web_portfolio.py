from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import yfinance as yf
import plotly
import datetime
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

PORTFOLIO_FILE = "portfolios.json"
TRANSACTION_FILE = "transactions.json"

# --- Helper functions (reuse your logic) ---
def fetch_current_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return float(price)
    except Exception:
        return None

def fetch_historical_prices(symbol, days=5):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=f"{days}d")
        return [float(p) for p in hist["Close"].tolist()]
    except Exception:
        return []

def load_all_portfolios():
    if not os.path.exists(PORTFOLIO_FILE):
        return {}
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)

def save_all_portfolios(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_all_transactions():
    if not os.path.exists(TRANSACTION_FILE):
        return {}
    with open(TRANSACTION_FILE, "r") as f:
        return json.load(f)

def save_all_transactions(data):
    with open(TRANSACTION_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Flask routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username'].strip().capitalize()
        return redirect(url_for('portfolio', username=username))
    return render_template('index.html')

@app.route('/portfolio/<username>', methods=['GET', 'POST'])
def portfolio(username):
    all_data = load_all_portfolios()
    all_transactions = load_all_transactions()
    portfolio = all_data.get(username, [])
    transactions = all_transactions.get(username, [])
    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        symbol = request.form.get('symbol', '').upper()
        shares = request.form.get('shares')
        cost_price = request.form.get('cost_price')
        idx = request.form.get('idx')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if action == 'add':
            if fetch_current_price(symbol) is None:
                flash(f"{symbol} not found or unavailable.", 'danger')
            else:
                try:
                    shares = int(shares)
                    cost_price = float(cost_price)
                    found = False
                    for stock in portfolio:
                        if stock['symbol'] == symbol:
                            total_shares = stock['shares'] + shares
                            stock['cost_price'] = (
                                (stock['cost_price'] * stock['shares'] + cost_price * shares) / total_shares
                            )
                            stock['shares'] = total_shares
                            found = True
                            break
                    if not found:
                        portfolio.append({
                            'symbol': symbol,
                            'shares': shares,
                            'cost_price': cost_price
                        })
                    transactions.append({
                        'action': 'buy',
                        'symbol': symbol,
                        'shares': shares,
                        'price': cost_price,
                        'datetime': now
                    })
                    all_data[username] = portfolio
                    all_transactions[username] = transactions
                    save_all_portfolios(all_data)
                    save_all_transactions(all_transactions)
                    flash(f"Bought {shares} shares of {symbol}.", 'success')
                except Exception:
                    flash("Invalid input.", 'danger')
        elif action == 'sell':
            try:
                shares = int(shares)
                found = False
                for stock in portfolio:
                    if stock['symbol'] == symbol:
                        found = True
                        if shares > stock['shares']:
                            flash(f"You only have {stock['shares']} shares of {symbol}.", 'danger')
                            break
                        stock['shares'] -= shares
                        transactions.append({
                            'action': 'sell',
                            'symbol': symbol,
                            'shares': shares,
                            'price': fetch_current_price(symbol),
                            'datetime': now
                        })
                        flash(f"Sold {shares} shares of {symbol}.", 'success')
                        if stock['shares'] == 0:
                            portfolio.remove(stock)
                        break
                if not found:
                    flash(f"You do not own any shares of {symbol}.", 'danger')
                all_data[username] = portfolio
                all_transactions[username] = transactions
                save_all_portfolios(all_data)
                save_all_transactions(all_transactions)
            except Exception:
                flash("Invalid input.", 'danger')
        elif action == 'delete':
            idx = int(idx)
            if 0 <= idx < len(portfolio):
                removed = portfolio.pop(idx)
                all_data[username] = portfolio
                save_all_portfolios(all_data)
                flash(f"Removed {removed['symbol']} from portfolio.", 'info')
    # Calculate summary
    summary = []
    total_invested = 0
    total_current = 0
    periods_map = {
        "1 year": 1,
        "3 years": 2,
        "5 years": 3
    }
    future_predictions = []
    plotly_plots = []
    for stock in portfolio:
        symbol = stock['symbol']
        shares = stock['shares']
        cost = stock['cost_price']
        current = fetch_current_price(symbol)
        invested = shares * cost
        current_value = shares * current if current else 0
        gain = current_value - invested if current else 0
        # Fetch more history for Prophet
        history = fetch_historical_prices(symbol, days=30)
        predictions = {}
        future_prices = []
        if history and len(history) >= 10:
            try:
                from prophet import Prophet
                import pandas as pd
                # Prepare data for Prophet
                df = pd.DataFrame({
                    'ds': pd.date_range(end=pd.Timestamp.today(), periods=len(history)),
                    'y': history
                })
                model = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False)
                model.fit(df)
                # Forecast for 3 days
                future = model.make_future_dataframe(periods=3, freq='D')
                forecast = model.predict(future)
                # Plotly plot: history + forecast
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines+markers', name='History'))
                fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
                fig.update_layout(title=f"{symbol} Price Prediction (History + 3d Forecast)", xaxis_title="Date", yaxis_title="Price ($)", template="plotly_white", height=350)
                plot_html = pio.to_html(fig, full_html=False)
                plotly_plots.append({'symbol': symbol, 'plot_html': plot_html})
                # For table predictions: 1 day, 2 days, 3 days
                days_map = {"1 day": 1, "2 days": 2, "3 days": 3}
                for label, days_ahead in days_map.items():
                    try:
                        predicted_price = forecast.iloc[len(history)+days_ahead-1]['yhat']
                        predicted_value = shares * predicted_price
                        predictions[label] = {
                            'predicted_price': predicted_price,
                            'predicted_value': predicted_value,
                            'gain': predicted_value - invested
                        }
                    except Exception:
                        predictions[label] = None
            except Exception:
                predictions = {label: None for label in ["1 day", "2 days", "3 days"]}
        else:
            predictions = {label: None for label in ["1 day", "2 days", "3 days"]}
        future_predictions.append({
            'symbol': symbol,
            'predictions': predictions
        })
        summary.append({
            'symbol': symbol,
            'shares': shares,
            'cost': cost,
            'current': current,
            'invested': invested,
            'current_value': current_value,
            'gain': gain
        })
        total_invested += invested
        total_current += current_value
    overall_gain = total_current - total_invested
    return render_template('portfolio.html', username=username, portfolio=portfolio, summary=summary, total_invested=total_invested, total_current=total_current, overall_gain=overall_gain, transactions=transactions, future_predictions=future_predictions, periods_map={"1 day": 1, "2 days": 2, "3 days": 3}, plotly_plots=plotly_plots)

def predict_future_price(prices, periods):
    from prophet import Prophet
    import pandas as pd
    import numpy as np
    if not prices or len(prices) < 10:
        raise ValueError("Not enough historical data to predict (need at least 10 days).")
    df = pd.DataFrame({
        'ds': pd.date_range(end=pd.Timestamp.today(), periods=len(prices)),
        'y': prices
    })
    model = Prophet(daily_seasonality=False, yearly_seasonality=False, weekly_seasonality=False)
    model.fit(df)
    future = model.make_future_dataframe(periods=periods, freq='D')
    forecast = model.predict(future)
    predicted_price = forecast.iloc[-1]['yhat']
    return predicted_price

if __name__ == '__main__':
    app.run(debug=True)
