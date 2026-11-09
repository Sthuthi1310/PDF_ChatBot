
import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from backend.rag_pipeline import process_pdf, answer_question


pdf_routes = Blueprint("pdf_routes", __name__)


# ---------------------------------------
# 1. UPLOAD AND PROCESS PDF
# ---------------------------------------
@pdf_routes.route("/api/upload", methods=["POST"])
def upload_pdf():

    # Check whether a file was received
    if "file" not in request.files:
        return jsonify({
            "error": "No file received."
        }), 400

    file = request.files["file"]

    # Check whether a file was selected
    if file.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    # Validate PDF extension
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "error": "Only PDF files are allowed."
        }), 400

    # Secure the filename
    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "error": "Invalid filename."
        }), 400

    # Get upload folder
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(upload_folder, exist_ok=True)

    pdf_path = os.path.join(upload_folder, filename)

    try:
        # Save uploaded PDF
        file.save(pdf_path)

        # Process PDF using RAG pipeline
        result = process_pdf(pdf_path)

        # Return processing details
        return jsonify({
            "message": result["message"],
            "filename": filename,
            "total_characters": result["total_characters"],
            "total_chunks": result["total_chunks"],
            "text_preview": result["text_preview"],
            "chunks_preview": result["chunks_preview"]
        }), 200

    except Exception as error:

        return jsonify({
            "error": f"PDF processing failed: {str(error)}"
        }), 500


# ---------------------------------------
# 2. ASK QUESTIONS ABOUT UPLOADED PDF
# ---------------------------------------
@pdf_routes.route("/api/ask", methods=["POST"])
def ask_question():

    # Get JSON data from frontend
    data = request.get_json(silent=True)

    if not data or "question" not in data:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    # Get and validate question
    question = str(data["question"]).strip()

    if not question:
        return jsonify({
            "error": "Question cannot be empty."
        }), 400

    # Get conversation history
    chat_history = data.get("history", [])

    if not isinstance(chat_history, list):
        return jsonify({
            "error": "Invalid chat history."
        }), 400

    # Validate history messages
    for message in chat_history:

        if not isinstance(message, dict):
            return jsonify({
                "error": "Invalid chat history format."
            }), 400

        if message.get("role") not in ["user", "assistant"]:
            return jsonify({
                "error": "Invalid chat history role."
            }), 400

        if not isinstance(message.get("content"), str):
            return jsonify({
                "error": "Invalid chat history content."
            }), 400

    try:
        # Generate answer using RAG pipeline
        answer = answer_question(
            question,
            chat_history
        )

        # Return question and answer
        return jsonify({
            "question": question,
            "answer": answer
        }), 200

    except FileNotFoundError as error:

        return jsonify({
            "error": str(error)
        }), 404

    except Exception as error:

        return jsonify({
            "error": f"Failed to generate answer: {str(error)}"
        }), 500
