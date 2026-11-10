
import os
import time

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:
    genai = None


from document_processing.pdf_loader import extract_text
from document_processing.text_splitter import split_text

from embeddings.embedder import generate_embeddings

from vectorstore.vector_store import (
    save_vector_store,
    search_similar_chunks
)

from backend.reranker import DocumentReranker


# ---------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------

load_dotenv()


# ---------------------------------------
# 2. INITIALIZE CROSS-ENCODER
# ---------------------------------------

reranker = None


def get_reranker():

    global reranker

    if reranker is None:
        reranker = DocumentReranker()

    return reranker


# ---------------------------------------
# 3. PROCESS UPLOADED PDF
# ---------------------------------------

def process_pdf(pdf_path):

    print("Starting PDF processing...")

    # Extract text from PDF
    extracted_text = extract_text(pdf_path)

    if not extracted_text.strip():
        raise ValueError("No readable text found in the PDF.")

    print("PDF text extracted successfully!")

    # Split extracted text into chunks
    chunks = split_text(extracted_text)

    if not chunks:
        raise ValueError("No text chunks generated.")

    print(f"Total chunks created: {len(chunks)}")

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    print("Embeddings generated successfully!")

    # Save embeddings and chunks in FAISS
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
# 4. GENERATE ANSWER FROM PDF
#    USING DEEP LEARNING + RAG
# ---------------------------------------

def answer_question(question, chat_history=None):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if chat_history is None:
        chat_history = []

    # -----------------------------------
    # A. BUILD SEARCH QUERY
    # -----------------------------------

    search_query = question

    previous_answers = [
        message["content"]
        for message in chat_history
        if message.get("role") == "assistant"
        and isinstance(message.get("content"), str)
    ]

    if previous_answers:
        search_query = (
            previous_answers[-1][:500] + " " + question
        )

    # -----------------------------------
    # B. RETRIEVE CHUNKS USING FAISS
    # -----------------------------------

    print("Searching relevant PDF chunks...")

    relevant_chunks = search_similar_chunks(
        search_query,
        top_k=8
    )

    if not relevant_chunks:
        return "No relevant information found in the uploaded PDF."

    print(f"Retrieved {len(relevant_chunks)} candidate chunks.")

    # -----------------------------------
    # C. RERANK USING CROSS-ENCODER
    # -----------------------------------

    print("Starting Cross-Encoder reranking...")

    model = get_reranker()

    reranked_chunks = model.rerank(
        search_query,
        relevant_chunks,
        top_k=3
    )

    if not reranked_chunks:
        return "No relevant information found in the uploaded PDF."

    print("Cross-Encoder reranking completed!")

    # Combine the best-ranked chunks
    context = "\n\n".join(reranked_chunks)

    # -----------------------------------
    # D. GET GEMINI API KEY
    # -----------------------------------

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    # -----------------------------------
    # E. PREPARE CHAT HISTORY
    # -----------------------------------

    history_text = ""

    for message in chat_history[-6:]:

        role = message.get("role", "")
        content = message.get("content", "")

        if role in ["user", "assistant"] and isinstance(content, str):

            history_text += f"\n{role}: {content}"

    # -----------------------------------
    # F. PREPARE GEMINI PROMPT
    # -----------------------------------

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

    # -----------------------------------
    # G. GEMINI MODEL CONFIGURATION
    # -----------------------------------

    gemini_models = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite"
    ]

    last_error = None

    # -----------------------------------
    # H. GENERATE ANSWER USING NEW SDK
    #    WITH AUTOMATIC RETRIES
    # -----------------------------------

    if genai is not None and hasattr(genai, "Client"):

        try:

            client = genai.Client(api_key=api_key)

            for model_name in gemini_models:

                for attempt in range(3):

                    try:

                        print(
                            f"Generating answer using {model_name}..."
                        )

                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )

                        answer = getattr(response, "text", None)

                        if answer:
                            print("Answer generated successfully!")
                            return answer.strip()

                        last_error = ValueError(
                            "Gemini did not generate an answer."
                        )

                        break

                    except Exception as exc:

                        last_error = exc

                        error_message = str(exc).upper()

                        if (
                            "503" in error_message
                            or "UNAVAILABLE" in error_message
                        ):

                            wait_time = 2 ** (attempt + 1)

                            print(
                                f"Gemini temporarily unavailable. "
                                f"Attempt {attempt + 1}/3."
                            )

                            if attempt < 2:

                                print(
                                    f"Retrying in {wait_time} seconds..."
                                )

                                time.sleep(wait_time)
                                continue

                        else:

                            print(
                                f"Gemini model {model_name} failed: {exc}"
                            )

                        break

        except Exception as exc:

            last_error = exc

    # -----------------------------------
    # I. FALLBACK TO OLDER GOOGLE SDK
    # -----------------------------------

    else:

        try:

            import google.generativeai as google_generative_ai

            google_generative_ai.configure(api_key=api_key)

            for model_name in gemini_models:

                for attempt in range(3):

                    try:

                        model = google_generative_ai.GenerativeModel(
                            model_name
                        )

                        response = model.generate_content(prompt)

                        answer = getattr(response, "text", None)

                        if answer:
                            print("Answer generated successfully!")
                            return answer.strip()

                        last_error = ValueError(
                            "Gemini did not generate an answer."
                        )

                        break

                    except Exception as exc:

                        last_error = exc

                        error_message = str(exc).upper()

                        if (
                            "503" in error_message
                            or "UNAVAILABLE" in error_message
                        ):

                            wait_time = 2 ** (attempt + 1)

                            print(
                                f"Gemini temporarily unavailable. "
                                f"Attempt {attempt + 1}/3."
                            )

                            if attempt < 2:

                                print(
                                    f"Retrying in {wait_time} seconds..."
                                )

                                time.sleep(wait_time)
                                continue

                        else:

                            print(
                                f"Gemini model {model_name} failed: {exc}"
                            )

                        break

        except ImportError as exc:

            raise ImportError(
                "Google Generative AI SDK is not installed. "
                "Install google-genai or google-generativeai."
            ) from exc

    # -----------------------------------
    # J. HANDLE FINAL ERRORS
    # -----------------------------------

    if last_error is not None:
        raise last_error

    raise ValueError("Gemini did not generate an answer.")
