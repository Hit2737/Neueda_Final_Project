import json
import os
from openai import OpenAI

# Initialize OpenAI client
HISTORICAL_PRICES = {
    "AAPL": [150, 155, 160, 162, 158, 165, 170, 175, 180, 185, 190, 195, 200],
    "GOOGL": [2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300],
    "MSFT": [300, 305, 310, 315, 320, 325, 330, 335, 340, 345, 350, 355, 360],
    # Add more symbols as needed
}
client = OpenAI(
    api_key="your-openai-api-key",  # Replace this with your real API key
)

# File to store user portfolios
PORTFOLIO_FILE = "portfolios.json"

# Dummy historical and current stock prices
HISTORICAL_PRICES = {
    "AAPL": [165, 170, 172, 174, 175],
    "TSLA": [710, 705, 700, 695, 690],
    "GOOGL": [2700, 2720, 2750, 2780, 2800],
    "MSFT": [310, 315, 320, 325, 330]
}

CURRENT_PRICES = {
    "AAPL": HISTORICAL_PRICES["AAPL"][-1],
    "TSLA": HISTORICAL_PRICES["TSLA"][-1],
    "GOOGL": HISTORICAL_PRICES["GOOGL"][-1],
    "MSFT": HISTORICAL_PRICES["MSFT"][-1]
}


# 🔹 Load/Save Portfolios
def load_all_portfolios():
    if not os.path.exists(PORTFOLIO_FILE):
        return {}
    with open(PORTFOLIO_FILE, "r") as f:
        return json.load(f)

def save_all_portfolios(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=4)


# 🔹 Get portfolio from user
def get_user_portfolio():
    print("📈 Let's build your portfolio!\n")
    portfolio = []

    while True:
        symbol = input("Enter stock symbol (or 'done' to finish): ").upper()
        if symbol == 'DONE':
            break
        if symbol not in CURRENT_PRICES:
            print(f"⚠️  {symbol} not found. Try AAPL, TSLA, GOOGL, MSFT.")
            continue
        try:
            shares = int(input(f"Enter number of shares for {symbol}: "))
            cost_price = float(input(f"Enter buying price per share of {symbol}: $"))
            portfolio.append({
                "symbol": symbol,
                "shares": shares,
                "cost_price": cost_price
            })
        except ValueError:
            print("⚠️  Invalid input. Please enter numeric values.")
            continue

    return portfolio


# 🔹 Update Portfolio (Buy/Sell)
def update_portfolio(portfolio):
    while True:
        action = input("Would you like to 'buy', 'sell', or 'done'? ").strip().lower()
        if action == 'done':
            break
        if action not in ['buy', 'sell']:
            print("Please enter 'buy', 'sell', or 'done'.")
            continue

        symbol = input("Enter stock symbol: ").upper()
        if symbol not in CURRENT_PRICES:
            print(f"⚠️  {symbol} not found. Try AAPL, TSLA, GOOGL, MSFT.")
            continue

        try:
            shares = int(input("Enter number of shares: "))
            if shares <= 0:
                print("Number of shares must be positive.")
                continue
        except ValueError:
            print("⚠️  Invalid input. Please enter a numeric value for shares.")
            continue

        if action == 'buy':
            cost_price = float(input(f"Enter buying price per share of {symbol}: $"))
            found = False
            for stock in portfolio:
                if stock["symbol"] == symbol:
                    total_shares = stock["shares"] + shares
                    stock["cost_price"] = (
                        (stock["cost_price"] * stock["shares"] + cost_price * shares) / total_shares
                    )
                    stock["shares"] = total_shares
                    found = True
                    break
            if not found:
                portfolio.append({
                    "symbol": symbol,
                    "shares": shares,
                    "cost_price": cost_price
                })
            print(f"✅ Bought {shares} shares of {symbol}.")
        elif action == 'sell':
            found = False
            for stock in portfolio:
                if stock["symbol"] == symbol:
                    found = True
                    if shares > stock["shares"]:
                        print(f"⚠️  You only have {stock['shares']} shares of {symbol}.")
                        break
                    stock["shares"] -= shares
                    print(f"✅ Sold {shares} shares of {symbol}.")
                    if stock["shares"] == 0:
                        portfolio.remove(stock)
                    break
            if not found:
                print(f"⚠️  You do not own any shares of {symbol}.")
    return portfolio


# 🔹 Calculate & Show Portfolio Performance
def predict_future_price(prices, periods):
    import numpy as np
    if not prices or len(prices) < 2:
        raise ValueError("Not enough historical data to predict.")
    x = np.arange(len(prices))
    y = np.array(prices)
    coeffs = np.polyfit(x, y, 1)  # Linear fit
    future_x = len(prices) + periods
    predicted_price = coeffs[0] * future_x + coeffs[1]
    return predicted_price
    
def calculate_portfolio_value(portfolio):
    total_invested = 0
    total_current = 0
    highest_gain = None
    lowest_gain = None

    print("\n📊 Portfolio Performance:")
    for stock in portfolio:
        symbol = stock["symbol"]
        shares = stock["shares"]
        cost = stock["cost_price"]
        current = CURRENT_PRICES[symbol]

        invested_value = shares * cost
        current_value = shares * current
        gain_loss = current_value - invested_value

        if highest_gain is None or gain_loss > highest_gain['gain']:
            highest_gain = {"symbol": symbol, "gain": gain_loss}
        if lowest_gain is None or gain_loss < lowest_gain['gain']:
            lowest_gain = {"symbol": symbol, "gain": gain_loss}

        total_invested += invested_value
        total_current += current_value

        status = "gain" if gain_loss >= 0 else "loss"
        print(f"- {symbol}: {shares} shares")
        print(f"  Bought at ${cost:.2f}, Current ${current:.2f}")
        print(f"  ➤ {status.upper()}: ${gain_loss:.2f}")

        # Historical trend
        history = HISTORICAL_PRICES[symbol]
        trend = "↑" if history[-1] > history[0] else "↓"
        print(f"  5-Day Trend: {trend} ({' → '.join([str(p) for p in history])})\n")

    overall_gain = total_current - total_invested

    print("💼 Portfolio Summary")
    print(f"  Total Invested: ${total_invested:.2f}")
    print(f"  Current Value:  ${total_current:.2f}")
    print(f"  Overall Gain/Loss: ${overall_gain:.2f}")

    # Generate LLM summary
    generate_ai_summary(portfolio, overall_gain)


def predict_portfolio_returns(portfolio):
    print("\n🔮 Predicted Returns (Simple Linear Model):")
    periods_map = {
        "1 year":  12,    # 12 months
        "3 years": 36,    # 36 months
        "5 years": 60     # 60 months
    }
    total_predicted = {k: 0 for k in periods_map}
    total_invested = 0

    for stock in portfolio:
        symbol = stock["symbol"]
        shares = stock["shares"]
        cost = stock["cost_price"]
        history = HISTORICAL_PRICES[symbol]
        invested = shares * cost
        total_invested += invested

        print(f"\n{symbol}:")
        for label, periods in periods_map.items():
            predicted_price = predict_future_price(history, periods)
            predicted_value = shares * predicted_price
            gain = predicted_value - invested
            print(f"  {label}: Predicted price ${predicted_price:.2f}, Predicted gain/loss: ${gain:.2f}")
            total_predicted[label] += predicted_value

    print("\n💼 Portfolio Predicted Summary:")
    for label in periods_map:
        overall_gain = total_predicted[label] - total_invested
        print(f"  {label}: Predicted overall gain/loss: ${overall_gain:.2f}")

# 🔹 OpenAI Summary Generator
def generate_ai_summary(portfolio, total_gain):
    prompt = "Here's the user's portfolio:\n"
    for stock in portfolio:
        symbol = stock["symbol"]
        shares = stock["shares"]
        cost = stock["cost_price"]
        current = CURRENT_PRICES[symbol]
        prompt += f"{symbol}: {shares} shares, bought at ${cost}, current price ${current}\n"

    prompt += f"\nTotal portfolio gain/loss: ${total_gain:.2f}\n"
    prompt += "Please write a concise summary of their portfolio performance and give 1 suggestion."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful investment advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        summary = response.choices[0].message.content
        print("\n💬 AI Summary (OpenAI):")
        print(summary)
    except Exception as e:
        print(f"\n⚠️ OpenAI API error: {e}")


# 🔹 Main Entry Point
def main():
    print("👤 Welcome to Portfolio Tracker!")
    username = input("Enter your name: ").strip().capitalize()

    all_data = load_all_portfolios()
    if username in all_data:
        print(f"🔄 Welcome back, {username}!")
        portfolio = all_data[username]
        choice = input("Do you want to buy or sell stocks? (yes/no): ").strip().lower()
        if choice == 'yes':
            portfolio = update_portfolio(portfolio)
            all_data[username] = portfolio
            save_all_portfolios(all_data)
    else:
        print(f"👋 Hello {username}, let's set up your portfolio.")
        portfolio = get_user_portfolio()
        all_data[username] = portfolio
        save_all_portfolios(all_data)

    if portfolio:
        calculate_portfolio_value(portfolio)
        predict_portfolio_returns(portfolio)
    else:
        print("⚠️  No valid stock entries provided.")


# Run script
if __name__ == "__main__":
    main()
