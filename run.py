# Fresh start with working app that has functional subscription payments
from working_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)