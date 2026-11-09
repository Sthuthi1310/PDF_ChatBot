
import os
from dotenv import load_dotenv

try:
    from google import genai
except ImportError:  # pragma: no cover - fallback for the older SDK
    genai = None

from document_processing.pdf_loader import extract_text
from document_processing.text_splitter import split_text
from embeddings.embedder import generate_embeddings
from vectorstore.vector_store import save_vector_store, search_similar_chunks


# Load environment variables from .env
load_dotenv()


# ---------------------------------------
# 1. PROCESS UPLOADED PDF
# ---------------------------------------
def process_pdf(pdf_path):

    print("Starting PDF processing...")

    # Extract text
    extracted_text = extract_text(pdf_path)

    if not extracted_text.strip():
        raise ValueError("No readable text found in the PDF.")

    print("PDF text extracted successfully!")

    # Split text into chunks
    chunks = split_text(extracted_text)

    if not chunks:
        raise ValueError("No text chunks generated.")

    print(f"Total chunks created: {len(chunks)}")

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    print("Embeddings generated successfully!")

    # Save embeddings and chunks
    save_vector_store(embeddings, chunks)

    print("RAG pipeline completed successfully!")

    return {
        "total_characters": len(extracted_text),
        "total_chunks": len(chunks),
        "text_preview": extracted_text[:3000],
        "chunks_preview": chunks[:3],
        "message": "PDF processed and vector store created successfully!"
    }


# ---------------------------------------
# 2. GENERATE ANSWER FROM PDF
# ---------------------------------------

# ---------------------------------------
# 2. GENERATE ANSWER WITH CHAT HISTORY
# ---------------------------------------
def answer_question(question, chat_history=None):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if chat_history is None:
        chat_history = []

    # Build a better search query using previous context
    search_query = question

    previous_answers = [
        message["content"]
        for message in chat_history
        if message.get("role") == "assistant"
    ]

    if previous_answers:
        search_query = (
            previous_answers[-1][:500] + " " + question
        )

    # Retrieve relevant chunks from FAISS
    relevant_chunks = search_similar_chunks(
        search_query,
        top_k=3
    )

    if not relevant_chunks:
        return "No relevant information found in the uploaded PDF."

    # Combine retrieved chunks
    context = "\n\n".join(relevant_chunks)

    # Get Gemini API key (support both naming conventions)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    # Prepare recent conversation history
    history_text = ""

    for message in chat_history[-6:]:

        role = message.get("role", "")

        content = message.get("content", "")

        if role in ["user", "assistant"] and isinstance(content, str):
            history_text += f"\n{role}: {content}"

    # Prepare prompt
    prompt = f"""
    You are a helpful PDF question-answering assistant.

    Use the conversation history to understand follow-up questions.

    Answer using ONLY the information available in the
    retrieved PDF context.

    If the answer is not available in the context,
    clearly say that the information is not available
    in the uploaded PDF.

    Previous Conversation:
    {history_text}

    Retrieved PDF Context:
    {context}

    Current User Question:
    {question}

    Answer:
    """

    gemini_models = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]

    last_error = None

    if genai is not None and hasattr(genai, "Client"):
        try:
            client = genai.Client(api_key=api_key)
            for model_name in gemini_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    answer = getattr(response, "text", None)
                    if answer:
                        return answer.strip()
                    last_error = ValueError("Gemini did not generate an answer.")
                except Exception as exc:
                    print(f"Gemini model {model_name} failed: {exc}")
                    last_error = exc
                    continue
        except Exception as exc:
            last_error = exc
    else:
        try:
            import google.generativeai as google_generative_ai
            google_generative_ai.configure(api_key=api_key)

            for model_name in gemini_models:
                try:
                    model = google_generative_ai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    answer = getattr(response, "text", None)
                    if answer:
                        return answer.strip()
                    last_error = ValueError("Gemini did not generate an answer.")
                except Exception as exc:
                    print(f"Gemini model {model_name} failed: {exc}")
                    last_error = exc
                    continue
        except ImportError as exc:
            raise ImportError(
                "Google Generative AI SDK is not installed. Install 'google-genai' or 'google-generativeai'."
            ) from exc

    if last_error is not None:
        raise last_error

    raise ValueError("Gemini did not generate an answer.")

