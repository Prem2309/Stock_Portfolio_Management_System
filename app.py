import os
import time
from flask import Flask, render_template_string, request, redirect, send_file, url_for
import pandas as pd

# Use non-interactive backend for matplotlib in web servers
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
print("[OK] 'static' folder verified!")

app = Flask(__name__)

# Portfolio data store
portfolio = [
    # Initial sample data for immediate preview (can be cleared or modified)
    {'ticker': 'RELIANCE', 'buy_price': 2400.0, 'quantity': 15, 'current_price': 2750.0},
    {'ticker': 'TCS', 'buy_price': 3500.0, 'quantity': 10, 'current_price': 3920.0},
    {'ticker': 'INFY', 'buy_price': 1600.0, 'quantity': 25, 'current_price': 1510.0},
    {'ticker': 'HDFCBANK', 'buy_price': 1550.0, 'quantity': 20, 'current_price': 1680.0}
]

def calculate_metrics():
    """Helper to compute portfolio financial metrics."""
    total_invested = sum(s['buy_price'] * s['quantity'] for s in portfolio)
    total_current = sum(s['current_price'] * s['quantity'] for s in portfolio)
    total_profit = total_current - total_invested
    profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0.0

    # Enrich each stock with individual metrics
    enriched_portfolio = []
    for s in portfolio:
        invested = s['buy_price'] * s['quantity']
        cur_val = s['current_price'] * s['quantity']
        pnl = cur_val - invested
        pnl_pct = ((s['current_price'] - s['buy_price']) / s['buy_price'] * 100) if s['buy_price'] > 0 else 0.0
        enriched_portfolio.append({
            **s,
            'invested': round(invested, 2),
            'current_val': round(cur_val, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': round(pnl_pct, 2)
        })

    return {
        'total_invested': round(total_invested, 2),
        'total_current': round(total_current, 2),
        'total_profit': round(total_profit, 2),
        'profit_pct': round(profit_pct, 2),
        'count': len(portfolio),
        'stocks': enriched_portfolio
    }

def generate_chart_file():
    """Generate modern donut chart and save to static/chart.png"""
    if not portfolio:
        return False
    
    labels = [s['ticker'] for s in portfolio]
    sizes = [s['quantity'] * s['current_price'] for s in portfolio]
    
    # Modern color palette
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#6366f1', '#14b8a6']
    
    fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(aspect="equal"))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        pctdistance=0.75,
        colors=colors[:len(labels)],
        textprops=dict(color="#1e293b", weight="bold"),
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10, weight="bold")
    ax.set_title("Portfolio Value Allocation", fontsize=13, weight="bold", pad=15, color="#0f172a")
    
    path = os.path.join('static', 'chart.png')
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return True

# --- HTML TEMPLATES ---

BASE_HEAD = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockVault — Portfolio Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen text-slate-800 flex flex-col justify-between">
    <!-- Navbar -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
            <a href="/" class="flex items-center gap-2.5">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                    <i class="fa-solid fa-chart-line text-lg"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-slate-900 leading-none">StockVault</h1>
                    <span class="text-xs text-slate-500 font-medium">Portfolio Intelligence</span>
                </div>
            </a>
            
            <nav class="flex items-center flex-wrap gap-2 text-sm font-semibold">
                <a href="/" class="px-3 py-1.5 rounded-lg text-slate-700 hover:text-blue-600 hover:bg-slate-100 transition"><i class="fa-solid fa-home mr-1.5 text-slate-400"></i>Dashboard</a>
                <a href="/summary" class="px-3 py-1.5 rounded-lg text-slate-700 hover:text-blue-600 hover:bg-slate-100 transition"><i class="fa-solid fa-file-invoice mr-1.5 text-slate-400"></i>Summary</a>
                <a href="/sort" class="px-3 py-1.5 rounded-lg text-slate-700 hover:text-blue-600 hover:bg-slate-100 transition"><i class="fa-solid fa-arrow-down-short-wide mr-1.5 text-slate-400"></i>Rankings</a>
                <a href="/chart" class="px-3 py-1.5 rounded-lg text-slate-700 hover:text-blue-600 hover:bg-slate-100 transition"><i class="fa-solid fa-pie-chart mr-1.5 text-slate-400"></i>Chart</a>
                
                <div class="h-4 w-px bg-slate-300 mx-1"></div>
                
                <a href="/download_zip" class="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition flex items-center gap-1.5 shadow-sm">
                    <i class="fa-solid fa-file-zipper"></i> ZIP
                </a>
                <a href="/export_csv" class="px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition flex items-center gap-1.5 shadow-sm">
                    <i class="fa-solid fa-file-csv"></i> CSV
                </a>
                <a href="/export_pdf" class="px-3 py-1.5 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition flex items-center gap-1.5 shadow-sm">
                    <i class="fa-solid fa-file-pdf"></i> PDF
                </a>
            </nav>
        </div>
    </header>
'''

BASE_FOOT = '''
    <footer class="bg-white border-t border-slate-200 mt-12 py-6 text-center text-xs text-slate-500 font-medium">
        <p>StockVault Portfolio Management System • Built with Flask & Tailwind CSS</p>
    </footer>
</body>
</html>
'''

MAIN_PAGE = BASE_HEAD + '''
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full flex-grow">
        
        <!-- Metrics Banner -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <!-- Total Value -->
            <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Portfolio Value</span>
                    <div class="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-sm">
                        <i class="fa-solid fa-wallet"></i>
                    </div>
                </div>
                <div class="text-2xl font-extrabold text-slate-900">₹{{ "{:,.2f}".format(metrics.total_current) }}</div>
                <div class="text-xs text-slate-500 mt-1">Live market valuation</div>
            </div>

            <!-- Total Invested -->
            <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Invested</span>
                    <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-sm">
                        <i class="fa-solid fa-coins"></i>
                    </div>
                </div>
                <div class="text-2xl font-extrabold text-slate-900">₹{{ "{:,.2f}".format(metrics.total_invested) }}</div>
                <div class="text-xs text-slate-500 mt-1">Cost basis across holdings</div>
            </div>

            <!-- Overall P&L -->
            <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Return (P&L)</span>
                    <div class="w-8 h-8 rounded-lg {{ 'bg-emerald-50 text-emerald-600' if metrics.total_profit >= 0 else 'bg-rose-50 text-rose-600' }} flex items-center justify-center text-sm">
                        <i class="fa-solid {{ 'fa-arrow-trend-up' if metrics.total_profit >= 0 else 'fa-arrow-trend-down' }}"></i>
                    </div>
                </div>
                <div class="text-2xl font-extrabold {{ 'text-emerald-600' if metrics.total_profit >= 0 else 'text-rose-600' }}">
                    {{ '+' if metrics.total_profit > 0 else '' }}₹{{ "{:,.2f}".format(metrics.total_profit) }}
                </div>
                <div class="mt-1 flex items-center gap-1.5 text-xs font-semibold {{ 'text-emerald-600' if metrics.total_profit >= 0 else 'text-rose-600' }}">
                    <span>{{ '+' if metrics.profit_pct > 0 else '' }}{{ metrics.profit_pct }}%</span>
                    <span class="text-slate-400 font-normal">all-time gain</span>
                </div>
            </div>

            <!-- Holdings Count -->
            <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Holdings</span>
                    <div class="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center text-sm">
                        <i class="fa-solid fa-layer-group"></i>
                    </div>
                </div>
                <div class="text-2xl font-extrabold text-slate-900">{{ metrics.count }}</div>
                <div class="text-xs text-slate-500 mt-1">Unique assets tracked</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <!-- Left 2 Cols: Holdings Table -->
            <div class="lg:col-span-2 space-y-6">
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <div class="px-6 py-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block"></span>
                            <h2 class="font-bold text-slate-900 text-base">Your Portfolio Holdings</h2>
                        </div>
                        <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">{{ metrics.count }} Stocks</span>
                    </div>

                    {% if metrics.stocks %}
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-sm text-slate-600">
                            <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="px-5 py-3.5">Ticker</th>
                                    <th class="px-4 py-3.5 text-right">Qty</th>
                                    <th class="px-4 py-3.5 text-right">Buy Price</th>
                                    <th class="px-4 py-3.5 text-right">Current</th>
                                    <th class="px-4 py-3.5 text-right">Holdings Value</th>
                                    <th class="px-4 py-3.5 text-right">P&L</th>
                                    <th class="px-4 py-3.5 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 font-medium">
                                {% for s in metrics.stocks %}
                                <tr class="hover:bg-slate-50/80 transition">
                                    <td class="px-5 py-4 whitespace-nowrap">
                                        <div class="flex items-center gap-2">
                                            <span class="font-extrabold text-slate-900 tracking-tight px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 text-xs border border-blue-100">
                                                {{ s.ticker }}
                                            </span>
                                        </div>
                                    </td>
                                    <td class="px-4 py-4 text-right font-semibold text-slate-800">{{ s.quantity }}</td>
                                    <td class="px-4 py-4 text-right text-slate-600">₹{{ "{:,.2f}".format(s.buy_price) }}</td>
                                    <td class="px-4 py-4 text-right font-semibold text-slate-900">₹{{ "{:,.2f}".format(s.current_price) }}</td>
                                    <td class="px-4 py-4 text-right font-bold text-slate-900">₹{{ "{:,.2f}".format(s.current_val) }}</td>
                                    <td class="px-4 py-4 text-right">
                                        <div class="{{ 'text-emerald-600' if s.pnl >= 0 else 'text-rose-600' }} font-bold text-xs">
                                            {{ '+' if s.pnl > 0 else '' }}₹{{ "{:,.2f}".format(s.pnl) }}
                                        </div>
                                        <div class="text-[11px] font-semibold {{ 'text-emerald-500' if s.pnl >= 0 else 'text-rose-500' }}">
                                            {{ '+' if s.pnl_pct > 0 else '' }}{{ s.pnl_pct }}%
                                        </div>
                                    </td>
                                    <td class="px-4 py-4 text-center">
                                        <form method="post" action="/remove" onsubmit="return confirm('Remove {{ s.ticker }} from portfolio?');" class="inline">
                                            <input type="hidden" name="ticker" value="{{ s.ticker }}">
                                            <button type="submit" title="Remove Stock" class="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100 transition inline-flex items-center justify-center text-xs">
                                                <i class="fa-solid fa-trash-can"></i>
                                            </button>
                                        </form>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <div class="text-center py-14 px-4">
                        <div class="w-14 h-14 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center mx-auto mb-3 text-xl">
                            <i class="fa-solid fa-arrow-trend-up"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-800">No stocks in your portfolio</h3>
                        <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1">Use the quick add form on the right to start tracking your first investment!</p>
                    </div>
                    {% endif %}
                </div>

                <!-- Allocation Chart Card -->
                <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                            <i class="fa-solid fa-chart-pie text-indigo-500"></i> Asset Distribution
                        </h3>
                        <a href="/chart" class="text-xs font-semibold text-blue-600 hover:text-blue-800">View Full Chart →</a>
                    </div>
                    {% if metrics.stocks %}
                    <div class="flex justify-center items-center">
                        <img src="/static/chart.png?v={{ timestamp }}" alt="Allocation Chart" class="max-h-72 object-contain rounded-xl">
                    </div>
                    {% else %}
                    <div class="text-center py-10 text-slate-400 text-xs">
                        Chart will appear once stocks are added.
                    </div>
                    {% endif %}
                </div>
            </div>

            <!-- Right Col: Action Forms -->
            <div class="space-y-6">

                <!-- Add Stock Card -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex items-center gap-2.5 mb-4">
                        <div class="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-sm">
                            <i class="fa-solid fa-plus"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-base">Add New Stock</h3>
                            <p class="text-xs text-slate-500">Record a new purchase</p>
                        </div>
                    </div>

                    <form method="post" action="/add" class="space-y-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Ticker Symbol</label>
                            <input name="ticker" placeholder="e.g. RELIANCE, AAPL" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition uppercase font-semibold">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Buy Price (₹)</label>
                                <input name="buy_price" placeholder="0.00" type="number" step="0.01" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Quantity</label>
                                <input name="quantity" placeholder="10" type="number" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Current Price (₹)</label>
                            <input name="current_price" placeholder="0.00" type="number" step="0.01" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
                        </div>
                        <button type="submit" class="w-full py-2.5 mt-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md shadow-blue-500/20 transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-check"></i> Add Stock
                        </button>
                    </form>
                </div>

                <!-- Update Stock Card -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex items-center gap-2.5 mb-4">
                        <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-sm">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-base">Update Holding</h3>
                            <p class="text-xs text-slate-500">Revise quantity or market price</p>
                        </div>
                    </div>

                    <form method="post" action="/update" class="space-y-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Ticker</label>
                            <input name="ticker" placeholder="Ticker to Update" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition uppercase font-semibold">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs font-bold text-slate-600 uppercase mb-1">New Quantity</label>
                                <input name="quantity" placeholder="New Qty" type="number" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-600 uppercase mb-1">New Price (₹)</label>
                                <input name="current_price" placeholder="New Price" type="number" step="0.01" required class="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition">
                            </div>
                        </div>
                        <button type="submit" class="w-full py-2.5 mt-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-sm shadow-md shadow-indigo-500/20 transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-arrows-rotate"></i> Update Stock
                        </button>
                    </form>
                </div>

                <!-- Search Stock Card -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex items-center gap-2.5 mb-4">
                        <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center text-sm">
                            <i class="fa-solid fa-magnifying-glass"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-base">Search Holding</h3>
                            <p class="text-xs text-slate-500">Lookup details for a symbol</p>
                        </div>
                    </div>

                    <form method="post" action="/search" class="flex gap-2">
                        <input name="ticker" placeholder="Search Ticker..." required class="flex-grow px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent transition uppercase font-semibold">
                        <button type="submit" class="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-sm shadow-md shadow-amber-500/20 transition">
                            Search
                        </button>
                    </form>
                </div>

                <!-- Remove Stock Card -->
                <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                    <div class="flex items-center gap-2.5 mb-4">
                        <div class="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center text-sm">
                            <i class="fa-solid fa-trash"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-slate-900 text-base">Remove Holding</h3>
                            <p class="text-xs text-slate-500">Delete an asset by symbol</p>
                        </div>
                    </div>

                    <form method="post" action="/remove" onsubmit="return confirm('Remove this stock?');" class="flex gap-2">
                        <input name="ticker" placeholder="Ticker to Delete" required class="flex-grow px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-transparent transition uppercase font-semibold">
                        <button type="submit" class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm shadow-md shadow-rose-500/20 transition">
                            Delete
                        </button>
                    </form>
                </div>

            </div>
        </div>
    </main>
''' + BASE_FOOT

PAGE_SUMMARY = BASE_HEAD + '''
    <main class="max-w-3xl mx-auto px-4 sm:px-6 py-12 w-full flex-grow">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
            <div class="flex items-center justify-between border-b border-slate-100 pb-5 mb-6">
                <div>
                    <h2 class="text-2xl font-black text-slate-900">Portfolio Financial Summary</h2>
                    <p class="text-xs text-slate-500 mt-1">High-level investment performance snapshot</p>
                </div>
                <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl">
                    <i class="fa-solid fa-wallet"></i>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold uppercase text-slate-400">Total Invested</span>
                    <div class="text-xl font-black text-slate-900 mt-1">₹{{ "{:,.2f}".format(invested) }}</div>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold uppercase text-slate-400">Current Valuation</span>
                    <div class="text-xl font-black text-slate-900 mt-1">₹{{ "{:,.2f}".format(current) }}</div>
                </div>
                <div class="p-4 rounded-xl {{ 'bg-emerald-50 border border-emerald-100' if profit >= 0 else 'bg-rose-50 border border-rose-100' }}">
                    <span class="text-xs font-bold uppercase {{ 'text-emerald-600' if profit >= 0 else 'text-rose-600' }}">Net Return</span>
                    <div class="text-xl font-black {{ 'text-emerald-700' if profit >= 0 else 'text-rose-700' }} mt-1">
                        {{ '+' if profit > 0 else '' }}₹{{ "{:,.2f}".format(profit) }}
                    </div>
                </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-slate-100">
                <a href="/" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition">
                    ← Back to Dashboard
                </a>
                <div class="flex gap-2">
                    <a href="/export_csv" class="px-4 py-2 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 font-bold text-sm transition">
                        <i class="fa-solid fa-file-csv mr-1"></i> Export CSV
                    </a>
                </div>
            </div>
        </div>
    </main>
''' + BASE_FOOT

PAGE_SORT = BASE_HEAD + '''
    <main class="max-w-4xl mx-auto px-4 sm:px-6 py-12 w-full flex-grow">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
            <div class="flex items-center justify-between border-b border-slate-100 pb-5 mb-6">
                <div>
                    <h2 class="text-2xl font-black text-slate-900">Holdings Ranked by Return %</h2>
                    <p class="text-xs text-slate-500 mt-1">Sorted descending by percentage performance</p>
                </div>
                <a href="/" class="text-xs font-bold px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition">
                    ← Dashboard
                </a>
            </div>

            {% if sorted_stocks %}
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-slate-600">
                    <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold tracking-wider border-b border-slate-100">
                        <tr>
                            <th class="px-4 py-3">Rank</th>
                            <th class="px-4 py-3">Ticker</th>
                            <th class="px-4 py-3 text-right">Return %</th>
                            <th class="px-4 py-3 text-right">Profit / Loss</th>
                            <th class="px-4 py-3 text-right">Current Price</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 font-medium">
                        {% for s in sorted_stocks %}
                        <tr class="hover:bg-slate-50/80 transition">
                            <td class="px-4 py-3 font-bold text-slate-400">#{{ loop.index }}</td>
                            <td class="px-4 py-3">
                                <span class="font-extrabold text-blue-700 px-2.5 py-1 rounded-lg bg-blue-50 text-xs border border-blue-100">
                                    {{ s.ticker }}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-right font-extrabold {{ 'text-emerald-600' if s.profit_pct >= 0 else 'text-rose-600' }}">
                                {{ '+' if s.profit_pct > 0 else '' }}{{ "{:,.2f}".format(s.profit_pct) }}%
                            </td>
                            <td class="px-4 py-3 text-right font-bold {{ 'text-emerald-600' if s.profit_amount >= 0 else 'text-rose-600' }}">
                                {{ '+' if s.profit_amount > 0 else '' }}₹{{ "{:,.2f}".format(s.profit_amount) }}
                            </td>
                            <td class="px-4 py-3 text-right font-semibold text-slate-900">₹{{ "{:,.2f}".format(s.current_price) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-sm text-slate-500 py-6 text-center">No portfolio holdings to rank.</p>
            {% endif %}

            <div class="mt-8 pt-4 border-t border-slate-100">
                <a href="/" class="inline-block px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition">
                    ← Back to Dashboard
                </a>
            </div>
        </div>
    </main>
''' + BASE_FOOT

PAGE_SEARCH = BASE_HEAD + '''
    <main class="max-w-xl mx-auto px-4 py-12 w-full flex-grow">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
            {% if found %}
            <div class="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 text-2xl shadow-sm">
                <i class="fa-solid fa-building-columns"></i>
            </div>
            <h2 class="text-2xl font-black text-slate-900 mb-1">{{ stock.ticker }}</h2>
            <p class="text-xs font-semibold text-slate-400 mb-6 uppercase tracking-wider">Holding Details</p>

            <div class="grid grid-cols-2 gap-3 text-left mb-6">
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold text-slate-400 uppercase">Quantity</span>
                    <p class="text-lg font-bold text-slate-800 mt-1">{{ stock.quantity }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold text-slate-400 uppercase">Current Price</span>
                    <p class="text-lg font-bold text-slate-800 mt-1">₹{{ "{:,.2f}".format(stock.current_price) }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold text-slate-400 uppercase">Buy Price</span>
                    <p class="text-lg font-bold text-slate-800 mt-1">₹{{ "{:,.2f}".format(stock.buy_price) }}</p>
                </div>
                <div class="p-4 rounded-xl bg-slate-50 border border-slate-100">
                    <span class="text-xs font-bold text-slate-400 uppercase">Holding Value</span>
                    <p class="text-lg font-bold text-slate-800 mt-1">₹{{ "{:,.2f}".format(stock.quantity * stock.current_price) }}</p>
                </div>
            </div>
            {% else %}
            <div class="w-16 h-16 rounded-2xl bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-4 text-2xl">
                <i class="fa-solid fa-triangle-exclamation"></i>
            </div>
            <h2 class="text-xl font-bold text-slate-800 mb-1">Stock Not Found</h2>
            <p class="text-xs text-slate-500 mb-6">"{{ query }}" is not in your current portfolio.</p>
            {% endif %}

            <a href="/" class="inline-block px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md shadow-blue-500/20 transition">
                ← Back to Dashboard
            </a>
        </div>
    </main>
''' + BASE_FOOT

PAGE_CHART = BASE_HEAD + '''
    <main class="max-w-3xl mx-auto px-4 py-12 w-full flex-grow">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center">
            <h2 class="text-2xl font-black text-slate-900 mb-1">Asset Allocation Chart</h2>
            <p class="text-xs text-slate-500 mb-6">Percentage weighting based on current market values</p>

            <div class="flex justify-center mb-8">
                <img src="/static/chart.png?v={{ timestamp }}" alt="Portfolio Allocation Chart" class="max-w-full rounded-2xl border border-slate-100 shadow-sm">
            </div>

            <div class="flex justify-center gap-3">
                <a href="/" class="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm transition">
                    ← Back to Dashboard
                </a>
                <a href="/export_pdf" class="px-5 py-2.5 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 font-bold text-sm transition">
                    <i class="fa-solid fa-file-pdf mr-1"></i> Download PDF
                </a>
            </div>
        </div>
    </main>
''' + BASE_FOOT


# --- FLASK ROUTES ---

@app.route('/')
def index():
    generate_chart_file()
    metrics = calculate_metrics()
    return render_template_string(MAIN_PAGE, metrics=metrics, timestamp=int(time.time()))

@app.route('/add', methods=['POST'])
def add_stock():
    ticker = request.form.get('ticker', '').strip().upper()
    buy_price = float(request.form.get('buy_price', 0))
    quantity = int(request.form.get('quantity', 0))
    current_price = float(request.form.get('current_price', 0))

    if ticker and quantity > 0:
        portfolio.append({
            'ticker': ticker,
            'buy_price': buy_price,
            'quantity': quantity,
            'current_price': current_price
        })
    return redirect('/')

@app.route('/remove', methods=['POST'])
def remove_stock():
    ticker = request.form.get('ticker', '').strip().upper()
    global portfolio
    portfolio = [stock for stock in portfolio if stock['ticker'] != ticker]
    return redirect('/')

@app.route('/update', methods=['POST'])
def update_stock():
    ticker = request.form.get('ticker', '').strip().upper()
    new_qty = request.form.get('quantity')
    new_price = request.form.get('current_price')

    for stock in portfolio:
        if stock['ticker'] == ticker:
            if new_qty:
                stock['quantity'] = int(new_qty)
            if new_price:
                stock['current_price'] = float(new_price)
            break
    return redirect('/')

@app.route('/search', methods=['POST'])
def search_stock():
    ticker = request.form.get('ticker', '').strip().upper()
    found_stock = next((s for s in portfolio if s['ticker'] == ticker), None)
    return render_template_string(PAGE_SEARCH, found=bool(found_stock), stock=found_stock, query=ticker)

@app.route('/summary')
def summary():
    invested = sum(s['buy_price'] * s['quantity'] for s in portfolio)
    current = sum(s['current_price'] * s['quantity'] for s in portfolio)
    profit = current - invested
    return render_template_string(PAGE_SUMMARY, invested=invested, current=current, profit=profit)

@app.route('/sort')
def sort_portfolio():
    sorted_port = []
    for s in portfolio:
        profit_amount = (s['current_price'] - s['buy_price']) * s['quantity']
        profit_pct = ((s['current_price'] - s['buy_price']) / s['buy_price'] * 100) if s['buy_price'] > 0 else 0
        sorted_port.append({
            **s,
            'profit_amount': profit_amount,
            'profit_pct': profit_pct
        })
    sorted_port.sort(key=lambda s: s['profit_pct'], reverse=True)
    return render_template_string(PAGE_SORT, sorted_stocks=sorted_port)

@app.route('/download_zip')
def download_zip():
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'stock-portfolio-app.zip'))
    if not os.path.exists(zip_path):
        import shutil
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', os.path.dirname(__file__))
    return send_file(zip_path, as_attachment=True, download_name="stock-portfolio-app.zip")

@app.route('/export_csv')
def export_csv():
    if not portfolio:
        df = pd.DataFrame(columns=['ticker', 'buy_price', 'quantity', 'current_price'])
    else:
        df = pd.DataFrame(portfolio)
    path = 'portfolio.csv'
    df.to_csv(path, index=False)
    return send_file(path, as_attachment=True)

@app.route('/export_pdf')
def export_pdf():
    if not portfolio:
        df = pd.DataFrame([{"Message": "Portfolio is empty"}])
    else:
        df = pd.DataFrame(portfolio)

    fig, ax = plt.subplots(figsize=(8, max(2.5, len(portfolio) * 0.5 + 1.5)))
    ax.axis('off')
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.4)

    # Style table header and rows
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#2563eb')
            cell.set_text_props(color='white', weight='bold')
        else:
            cell.set_facecolor('#f8fafc' if row % 2 == 0 else '#ffffff')

    path = 'portfolio.pdf'
    fig.savefig(path, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return send_file(path, as_attachment=True)

@app.route('/chart')
def chart():
    if not portfolio:
        return render_template_string(BASE_HEAD + '''
            <main class="max-w-xl mx-auto px-4 py-16 text-center">
                <div class="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
                    <p class="text-slate-600 font-semibold mb-4">No data available to generate chart.</p>
                    <a href="/" class="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-bold">← Dashboard</a>
                </div>
            </main>
        ''' + BASE_FOOT)
    
    generate_chart_file()
    return render_template_string(PAGE_CHART, timestamp=int(time.time()))

if __name__ == '__main__':
    try:
        import IPython.display as display
        display.display(display.Markdown("[Click here to open the app](http://127.0.0.1:5000)"))
    except (ImportError, Exception):
        pass
    print("\n* StockVault App is running at: http://127.0.0.1:5000\n")
    app.run(debug=True)
