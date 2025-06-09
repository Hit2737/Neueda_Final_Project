const stockList = document.getElementById('stock-list');
const totalValueSpan = document.getElementById('total-value');
const stockSearchInput = document.getElementById('stock-search');
const searchResultsList = document.getElementById('search-results');
const transactionList = document.getElementById('transaction-list');

// Mock stock data
const mockStockData = [
    { symbol: 'AAPL', description: 'Apple Inc.', price: 150 },
    { symbol: 'GOOGL', description: 'Alphabet Inc.', price: 2800 },
    { symbol: 'AMZN', description: 'Amazon.com Inc.', price: 3500 },
    { symbol: 'MSFT', description: 'Microsoft Corporation', price: 300 },
    { symbol: 'TSLA', description: 'Tesla Inc.', price: 700 },
];

let portfolio = []; // In-memory portfolio
let transactionHistory = []; // In-memory transaction history

// Fetch and display portfolio
function fetchPortfolio() {
    if (!stockList) {
        console.error('Element with ID "stock-list" not found.');
        return;
    }

    stockList.innerHTML = ''; // Clear the stock list
    let totalValue = 0;

    portfolio.forEach((stock) => {
        const li = document.createElement('li');
        li.textContent = `${stock.name} - ${stock.quantity} shares @ $${stock.price.toFixed(2)} each (Total: $${stock.total.toFixed(2)})`;
        stockList.appendChild(li);
        totalValue += stock.total;
    });

    totalValueSpan.textContent = `$${totalValue.toFixed(2)}`; // Update total portfolio value
}

// Add a stock to the portfolio
function addStockToPortfolio(stockSymbol, quantity) {
    const stockData = mockStockData.find((stock) => stock.symbol === stockSymbol.toUpperCase());
    if (!stockData) {
        alert('Invalid stock symbol.');
        return;
    }

    const stockTotal = stockData.price * quantity; // Calculate total for the stock
    portfolio.push({ name: stockData.symbol, quantity, price: stockData.price, total: stockTotal });

    // Log the transaction
    transactionHistory.push({
        type: 'ADD',
        name: stockData.symbol,
        quantity,
        date: new Date().toISOString(),
    });

    fetchPortfolio(); // Refresh portfolio
    fetchTransactionHistory(); // Refresh transaction history
}

// Fetch and display transaction history
function fetchTransactionHistory() {
    if (!transactionList) {
        console.error('Element with ID "transaction-list" not found.');
        return;
    }

    transactionList.innerHTML = ''; // Clear the list

    transactionHistory.forEach((transaction) => {
        const li = document.createElement('li');
        li.textContent = `${transaction.type} ${transaction.quantity} shares of ${transaction.name} on ${new Date(transaction.date).toLocaleString()}`;
        transactionList.appendChild(li);
    });
}

// Search for stock symbols
stockSearchInput.addEventListener('input', () => {
    const query = stockSearchInput.value.trim().toUpperCase();

    if (query.length < 2) {
        searchResultsList.innerHTML = ''; // Clear results if query is too short
        return;
    }

    const results = mockStockData.filter((stock) => stock.symbol.includes(query) || stock.description.toUpperCase().includes(query));
    searchResultsList.innerHTML = ''; // Clear previous results

    results.forEach((stock) => {
        const card = document.createElement('div');
        card.className = 'stock-card';

        const stockInfo = document.createElement('div');
        stockInfo.className = 'stock-info';
        stockInfo.innerHTML = `<strong>${stock.symbol}</strong> - ${stock.description}<br>Price: $${stock.price.toFixed(2)}`;

        const quantityInput = document.createElement('input');
        quantityInput.type = 'number';
        quantityInput.min = 1;
        quantityInput.value = 1;
        quantityInput.className = 'quantity-input';

        const addButton = document.createElement('button');
        addButton.textContent = '+';
        addButton.className = 'add-button';
        addButton.addEventListener('click', () => {
            const quantity = parseInt(quantityInput.value);
            if (quantity > 0) {
                addStockToPortfolio(stock.symbol, quantity);
                searchResultsList.innerHTML = ''; // Clear search results
                stockSearchInput.value = ''; // Clear the search input
            } else {
                alert('Please enter a valid quantity.');
            }
        });

        card.appendChild(stockInfo);
        card.appendChild(quantityInput);
        card.appendChild(addButton);
        searchResultsList.appendChild(card);
    });
}

// Initial fetch
document.addEventListener('DOMContentLoaded', () => {
    fetchPortfolio(); // Ensure portfolio is initialized before calling this
    fetchTransactionHistory();
});