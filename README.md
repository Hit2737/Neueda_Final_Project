# Neueda Final Project

This project is part of the Neueda Training program and demonstrates the use of Git, GitHub, and Generative AI tools such as GitHub Copilot for modern software development.

## Project Overview

This is a Stock Portfolio Tracker application with both console and web-based interfaces. It allows users to:
- Track their stock portfolio (buy/sell, view performance)
- View transaction history
- Predict future stock prices using advanced ML (Prophet)
- Visualize historical and predicted prices with interactive plots (web app)

## Features
- **Console App** (`portfolio_tracker.py`):
  - Add, buy, and sell stocks
  - View portfolio performance and summary
  - Predict future returns using Prophet
  - Transaction logging (in web version)
- **Web App** (`web_portfolio.py`):
  - User-friendly web interface (Flask + Bootstrap)
  - Add, buy, and sell stocks
  - View and export portfolio
  - Transaction history table
  - Interactive Plotly charts for price history and 3-day Prophet forecast
  - Short-term (1, 2, 3 day) price predictions

## Tech Stack
- Python 3
- Flask (web framework)
- yfinance (stock data)
- Prophet (ML time series forecasting)
- Plotly (interactive charts)
- Bootstrap (UI)

## How to Run
1. **Install dependencies:**
   ```sh
   pip install flask yfinance prophet plotly
   ```
2. **Start the web app:**
   ```sh
   python3 web_portfolio.py
   ```
   Then open [http://localhost:5000](http://localhost:5000) in your browser.

3. **(Optional) Run the console app:**
   ```sh
   python3 portfolio_tracker.py
   ```

## Learning Outcomes
- Practical use of Git and GitHub for version control and collaboration
- Leveraging GenAI tools (GitHub Copilot) for code generation and productivity
- Building and deploying a real-world Python application with ML and visualization

---
*This project was developed as part of the Neueda Training program.*
