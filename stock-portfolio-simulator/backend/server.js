const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

let portfolio = []; // In-memory portfolio (use a database for persistence)

// Hardcoded stock prices
const stockPrices = {
    AAPL: 150, // Example: Apple stock price
    GOOGL: 200, // Example: Google stock price
    TSLA: 250, // Example: Tesla stock price
};

let transactionHistory = []; // In-memory transaction history

// Add a stock to the portfolio
app.post('/api/add-stock', (req, res) => {
    const { name, quantity } = req.body;
    portfolio.push({ name, quantity });

    // Log the transaction
    transactionHistory.push({
        type: 'ADD',
        name,
        quantity,
        date: new Date().toISOString(),
    });

    res.json({ message: 'Stock added successfully', portfolio });
});

// Get portfolio with real-time prices
app.get('/api/portfolio', (req, res) => {
    try {
        const updatedPortfolio = portfolio.map((stock) => {
            const price = stockPrices[stock.name] || 0; // Use hardcoded price
            return { ...stock, price, total: price * stock.quantity };
        });

        const totalValue = updatedPortfolio.reduce((acc, stock) => acc + stock.total, 0);
        const lowValueAlert = totalValue < 100; // Check if portfolio value is below $100

        res.json({ portfolio: updatedPortfolio, totalValue, lowValueAlert });
    } catch (error) {
        res.status(500).json({ message: 'Error calculating portfolio', error: error.message });
    }
});

// Get transaction history
app.get('/api/transaction-history', (req, res) => {
    res.json({ transactionHistory });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));