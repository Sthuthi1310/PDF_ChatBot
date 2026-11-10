# Intelligent PDF Question Answering Chatbot

An AI-powered PDF Question Answering Chatbot that allows users to upload PDF documents and ask questions about their contents. The system uses Retrieval-Augmented Generation (RAG), semantic search, document reranking, and two different question-answering models to generate and compare answers.

## Features

- **PDF Upload:** Upload PDF documents through a web interface.
- **Text Extraction:** Extract text from uploaded PDF files.
- **Text Chunking:** Divide extracted text into smaller chunks for efficient retrieval.
- **Semantic Embeddings:** Generate text embeddings using Sentence Transformers.
- **Vector Database:** Store and retrieve document chunks using FAISS.
- **Document Reranking:** Use a Cross-Encoder model to rerank retrieved chunks based on relevance.
- **Extractive Question Answering:** Use RoBERTa to extract answers directly from document text.
- **Generative Question Answering:** Use Google Gemini to generate detailed, natural-language answers.
- **Answer Comparison:** Display RoBERTa and Gemini answers separately for comparison.
- **Conversation History:** Support follow-up questions using previous conversation context.

## Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| PDF Processing | PDF text extraction |
| Text Embeddings | Sentence Transformers |
| Vector Database | FAISS |
| Reranking | Cross-Encoder |
| Extractive QA | RoBERTa (SQuAD2) |
| Generative QA | Google Gemini API |
| Deep Learning Framework | PyTorch |

## Models Used

### 1. Sentence Transformer

Used to convert document chunks into numerical embeddings for semantic similarity search.

### 2. Cross-Encoder

Model: `cross-encoder/ms-marco-MiniLM-L6-v2`

Used to rerank retrieved document chunks according to their relevance to the user's question.

### 3. RoBERTa

Model: `deepset/roberta-base-squad2`

Used for extractive question answering. It identifies answer spans directly from the retrieved document text.

### 4. Google Gemini

Used for generative question answering. It generates detailed and readable answers using the retrieved PDF context.

## System Architecture

The application follows a Retrieval-Augmented Generation (RAG) pipeline.

```text
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
              Embeddings
                    |
                    v
             FAISS Vector Store
                    |
                    |
             User Question
                    |
                    v
          Semantic Similarity Search
                    |
                    v
            Relevant Chunks
                    |
                    v
             Cross-Encoder
                Reranking
                    |
                    v
           Top Relevant Chunks
                    |
             +------+------+
             |             |
             v             v
          RoBERTa        Gemini
        Extractive     Generative
          Answer         Answer
             |             |
             +------+------+
                    |
                    v
          Display Both Answers
              in Frontend
```

## Project Structure

```text
PDF_ChatBot/
│
├── backend/
│   ├── app.py
│   ├── routes.py
│   ├── rag_pipeline.py
│   ├── reranker.py
│   └── qa_model.py
│
├── document_processing/
│   ├── pdf_loader.py
│   └── text_splitter.py
│
├── embeddings/
│   └── embedder.py
│
├── vectorstore/
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
├── requirements.txt
├── app.py
└── README.md
```

*Note: The structure above represents the main project modules. Generated files and additional utility modules may also exist.*

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Navigate to the project directory:

```bash
cd PDF_ChatBot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.env` file in the project root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Obtain an API key from [Google AI Studio](https://aistudio.google.com/).

### 5. Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5001
```

## How to Use

1. Start the Flask application.
2. Open the chatbot in your browser.
3. Upload a PDF document.
4. Wait for the document to be processed.
5. Enter a question related to the uploaded document.
6. View the answer generated by RoBERTa.
7. View the detailed answer generated by Gemini.
8. Ask follow-up questions to explore the document further.

## Answer Generation

The application uses two different question-answering approaches:

**RoBERTa – Extractive Question Answering**

RoBERTa identifies and extracts relevant answer spans from the retrieved document chunks.

**Gemini – Generative Question Answering**

Gemini uses the retrieved document context to generate detailed, natural-language responses.

Both answers are displayed separately, allowing users to compare extractive and generative question-answering approaches.

## Future Enhancements

- Improve RoBERTa answer extraction and no-answer detection.
- Improve handling of long document contexts.
- Evaluate answer accuracy using a larger set of test questions.
- Compare model performance using appropriate evaluation metrics.
- Improve response formatting and frontend presentation.
- Support multiple PDF documents.
- Add document-level conversation management.

## Security

- Keep API keys in environment variables.
- Exclude `.env` and virtual environment directories from version control.
- Validate uploaded file types.
- Use secure filenames for uploaded documents.

## License

This project is developed for academic and educational purposes.