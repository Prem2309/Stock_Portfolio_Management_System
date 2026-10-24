# StockVault — Modern Stock Portfolio Management System

A polished, modern web dashboard for tracking and analyzing stock investments built with Python, Flask, Tailwind CSS, Pandas, and Matplotlib.

## ✨ Enhancements & Features
- **Executive KPI Dashboard**: Instant visibility into Total Portfolio Valuation, Total Invested, Net Profit/Loss (₹ and %), and Asset Count.
- **Modern Holdings Table**: Formatted values, color-coded P&L indicators, and one-click removal with confirmation.
- **Embedded Donut Chart**: Dynamic asset allocation chart powered by Matplotlib with anti-cache busting.
- **Sleek Action Cards**: Quick forms for Adding, Updating, Searching, and Deleting stocks.
- **Dedicated Styled Views**: Redesigned `/summary`, `/sort` (ranked by return %), and `/search` views matching the fintech UI theme.
- **One-Click Exports**: Export portfolio reports to formatted CSV and styled PDF.
- **Server Stability**: Server-safe `matplotlib.use('Agg')` and `plt.close()` preventing memory leaks.

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install flask pandas matplotlib
```

### 2. Run Application
```bash
python app.py
```
Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.
