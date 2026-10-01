import os
from app import create_app

# Create application instance for Gunicorn and local development
app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Host on 0.0.0.0 for container & local network compatibility
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
