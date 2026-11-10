# Intelligent Document Question Answering System

An AI-powered PDF Question Answering System that allows users to upload PDF documents and ask questions based on their content. The system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate context-aware answers.

## Project Overview

Reading and searching through lengthy PDF documents can be time-consuming. This project simplifies the process by allowing users to interact with their documents through a question-answering interface.

The system extracts text from uploaded PDFs, divides it into smaller chunks, converts the chunks into vector embeddings, and stores them in a FAISS vector database. When a user asks a question, the system retrieves relevant chunks, reranks them using a Cross-Encoder model, and generates an answer using Google's Gemini API.

## Features

- **PDF Upload:** Upload PDF documents through a web interface.
- **Text Extraction:** Extract textual content from uploaded PDF files.
- **Text Chunking:** Split extracted text into smaller, manageable chunks.
- **Semantic Embeddings:** Generate embeddings using Sentence Transformers.
- **Vector Search:** Retrieve relevant document chunks using FAISS.
- **Cross-Encoder Reranking:** Improve retrieval relevance by reranking candidate chunks.
- **AI-Powered Answers:** Generate natural-language answers using Google Gemini.
- **Context-Aware Conversations:** Support follow-up questions using conversation history.
- **Flask Backend:** Handle document processing and question-answering requests through REST API endpoints.

## Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML, CSS, JavaScript |
| Text Extraction | PDF processing library |
| Text Embeddings | Sentence Transformers |
| Vector Database | FAISS |
| Reranking | Cross-Encoder |
| Language Model | Google Gemini API |
| Environment Management | Python Virtual Environment |

## System Architecture

```text
             PDF Document
                   |
                   v
             PDF Upload
                   |
                   v
             Text Extraction
                   |
                   v
              Text Chunking
                   |
                   v
          Sentence Transformer
             (Embeddings)
                   |
                   v
            FAISS Vector Store
                   |
                   v
             User Question
                   |
                   v
          Semantic Retrieval
          (Top 8 Candidates)
                   |
                   v
           Cross-Encoder
              Reranking
                   |
                   v
           Top 3 Relevant Chunks
                   |
                   v
             Gemini API
                   |
                   v
          Context-Based Answer
```

## Project Structure

```text
PDF_ChatBot/
│
├── backend/
│   ├── __init__.py
│   ├── routes.py
│   ├── rag_pipeline.py
│   └── reranker.py
│
├── document_processing/
│   ├── __init__.py
│   ├── pdf_loader.py
│   └── text_splitter.py
│
├── embeddings/
│   ├── __init__.py
│   └── embedder.py
│
├── vectorstore/
│   ├── __init__.py
│   └── vector_store.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── uploads/
│
├── .env
├── .gitignore
├── app.py
├── requirements.txt
└── README.md
```

*Note: Adjust the structure above if your actual project contains additional files or uses different folder names.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate into the project directory:

```bash
cd PDF_ChatBot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API Key

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_gemini_api_key` with your actual Google Gemini API key.

Keep the API key private. Do not upload the `.env` file to GitHub.

### 5. Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5001
```

## How It Works

### 1. Document Processing
The user uploads a PDF document. The system extracts its textual content and divides it into smaller chunks.

### 2. Embedding Generation
Sentence Transformers converts each text chunk into a numerical vector representation that captures its semantic meaning.

### 3. Vector Storage
The generated embeddings are stored in a FAISS vector index to support efficient similarity-based retrieval.

### 4. Relevant Information Retrieval
When a user submits a question, the system converts it into an embedding and retrieves the eight most relevant chunks from the vector store.

### 5. Cross-Encoder Reranking
The Cross-Encoder evaluates the question and retrieved chunks together, ranks them according to relevance, and selects the top three chunks.

### 6. Answer Generation
The selected chunks are passed as context to the Gemini API, which generates a natural-language answer based on the retrieved document content.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/upload` | POST | Upload and process a PDF document |
| `/api/ask` | POST | Submit a question and receive an answer |

## Models Used

| Model | Purpose |
|---|---|
| Sentence Transformer | Generate semantic embeddings |
| `cross-encoder/ms-marco-MiniLM-L6-v2` | Rerank retrieved document chunks |
| `gemini-3.5-flash` | Generate context-aware answers |

## Future Enhancements

- Integrate a RoBERTa-based extractive Question Answering model.
- Compare extractive answers with Gemini-generated answers.
- Improve answer accuracy through retrieval and model evaluation.
- Add support for multiple PDF documents.
- Improve conversation history management.
- Implement document-grounded responses with better handling of questions outside the uploaded content.
- Add performance evaluation using retrieval accuracy, answer quality, and response time.

## Author

**Sthuthi Sheela**

Computer Science and Engineering

## License

This project is intended for educational and academic purposes.