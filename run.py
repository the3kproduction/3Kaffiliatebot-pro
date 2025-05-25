import os

# Set environment flag for Render deployment early
if not os.environ.get('REPL_ID'):
    os.environ['RENDER'] = 'true'

from app import app

# Import clean routes that work without authentication issues
import render_routes  # noqa: F401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)