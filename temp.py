import yfinance as yf
data = yf.Ticker("MSFT")

# print(data.info)
print(data.quarterly_income_stmt)
print(data.history(period="1mo", interval="1d"))

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(data.history(period="1mo", interval="1d")['Close'])
plt.title("MSFT Stock Price - Last Month")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.xticks(rotation=45)
plt.grid()
plt.tight_layout()
plt.show()