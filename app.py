
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.routes import pdf_routes


# Get the project root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Initialize Flask application
app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path="/static"
)


# Application configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "rag-chatbot-dev-key"
)

app.config["UPLOAD_FOLDER"] = os.path.join(
    BASE_DIR, "uploads"
)

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


# Enable CORS
CORS(app)


# Create required directories if they don't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# Register backend routes
app.register_blueprint(pdf_routes)


# Home route - Serve frontend
@app.route("/")
def home():
    return send_from_directory(
        os.path.join(BASE_DIR, "frontend"),
        "index.html"
    )


# Handle oversized uploads
@app.errorhandler(413)
def file_too_large(error):
    return {"error": "File size exceeds the 16 MB limit"}, 413


# Run Flask application
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
