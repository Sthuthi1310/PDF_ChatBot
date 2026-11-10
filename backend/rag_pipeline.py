
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
from backend.qa_model import RoBERTaQuestionAnswering


# ---------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# ---------------------------------------

load_dotenv()


# ---------------------------------------
# 2. INITIALIZE MODELS
# ---------------------------------------

reranker = None
qa_model = None


def get_reranker():

    global reranker

    if reranker is None:
        reranker = DocumentReranker()

    return reranker


def get_qa_model():

    global qa_model

    if qa_model is None:
        qa_model = RoBERTaQuestionAnswering()

    return qa_model


# ---------------------------------------
# 3. PROCESS UPLOADED PDF
# ---------------------------------------

def process_pdf(pdf_path):

    print("Starting PDF processing...")

    # Extract text from PDF
    extracted_text = extract_text(pdf_path)

    if not extracted_text or not extracted_text.strip():
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
# 4. GENERATE ANSWERS FROM PDF
#    USING ROBERTA + GEMINI
# ---------------------------------------

def answer_question(question, chat_history=None):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    question = question.strip()

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

        return {
            "roberta_answer": "No relevant information found.",
            "roberta_score": 0.0,
            "gemini_answer": (
                "No relevant information found in the uploaded PDF."
            )
        }

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

        return {
            "roberta_answer": "No relevant information found.",
            "roberta_score": 0.0,
            "gemini_answer": (
                "No relevant information found in the uploaded PDF."
            )
        }

    print("Cross-Encoder reranking completed!")

    # Combine the best-ranked chunks for Gemini
    context = "\n\n".join(reranked_chunks)

    # -----------------------------------
    # D. GENERATE ANSWER USING ROBERTA
    # -----------------------------------

    print("Generating answer using RoBERTa...")

    roberta_result = {
        "answer": "No relevant answer found.",
        "score": 0.0
    }

    try:

        extractive_model = get_qa_model()

        roberta_results = []

        # Run RoBERTa on each retrieved chunk
        for chunk in reranked_chunks:

            try:

                result = extractive_model.answer(
                    question,
                    chunk
                )

                if (
                    result
                    and result.get("answer")
                    and result["answer"] != "No relevant answer found."
                ):

                    roberta_results.append(result)

            except Exception as exc:

                print(f"RoBERTa chunk processing failed: {exc}")

        # Select the result with the highest model score
        if roberta_results:

            roberta_result = max(
                roberta_results,
                key=lambda item: item.get("score", 0.0)
            )

        print("RoBERTa answer generation completed!")

    except Exception as exc:

        print(f"RoBERTa model failed: {exc}")
        print("Continuing with Gemini...")

    # -----------------------------------
    # E. GET GEMINI API KEY
    # -----------------------------------

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    # -----------------------------------
    # F. PREPARE CHAT HISTORY
    # -----------------------------------

    history_text = ""

    for message in chat_history[-6:]:

        role = message.get("role", "")
        content = message.get("content", "")

        if role in ["user", "assistant"] and isinstance(content, str):

            history_text += f"\n{role}: {content}"

    # -----------------------------------
    # G. PREPARE GEMINI PROMPT
    # -----------------------------------

    prompt = f"""
You are a helpful PDF question-answering assistant.

Use the conversation history to understand follow-up questions.

Answer using ONLY the information available in the
retrieved PDF context.

Do not introduce information from outside the PDF.

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
    # H. GEMINI MODEL CONFIGURATION
    # -----------------------------------

    gemini_models = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite"
    ]

    last_error = None

    # -----------------------------------
    # I. GENERATE ANSWER USING NEW SDK
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

                        if answer and answer.strip():

                            print("Gemini answer generated successfully!")

                            return {
                                "roberta_answer": roberta_result["answer"],
                                "roberta_score": roberta_result["score"],
                                "gemini_answer": answer.strip()
                            }

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
            print(f"New Gemini SDK failed: {exc}")

    # -----------------------------------
    # J. FALLBACK TO OLDER GOOGLE SDK
    # -----------------------------------

    else:

        try:

            import google.generativeai as google_generative_ai

            google_generative_ai.configure(api_key=api_key)

            for model_name in gemini_models:

                for attempt in range(3):

                    try:

                        print(
                            f"Generating answer using {model_name}..."
                        )

                        model = google_generative_ai.GenerativeModel(
                            model_name
                        )

                        response = model.generate_content(prompt)

                        answer = getattr(response, "text", None)

                        if answer and answer.strip():

                            print("Gemini answer generated successfully!")

                            return {
                                "roberta_answer": roberta_result["answer"],
                                "roberta_score": roberta_result["score"],
                                "gemini_answer": answer.strip()
                            }

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
    # K. HANDLE FINAL ERRORS
    # -----------------------------------

    if last_error is not None:
        raise last_error

    raise ValueError("Gemini did not generate an answer.")
