import sys
import os

# Allow running from root folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api.index import app

if __name__ == '__main__':
    try:
        import IPython.display as display
        display.display(display.Markdown("[Click here to open the app](http://127.0.0.1:5000)"))
    except (ImportError, Exception):
        pass
    print("\n* StockVault App is running at: http://127.0.0.1:5000\n")
    app.run(debug=True)
