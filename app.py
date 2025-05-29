# Simple import file for Render deployment compatibility
from working_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)