# AI PDF Chatbot – Chat with Your PDF Using RAG

## 1. Project Overview

AI PDF Chatbot is a web-based application that allows users to upload PDF documents and ask questions based on their contents.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate accurate, context-based answers using Google's Gemini API.

Instead of answering questions using general knowledge, the chatbot retrieves relevant text from the uploaded PDF and uses it as context to generate responses.

## 2. Objectives

- Allow users to upload PDF documents through a web interface.
- Extract text from uploaded PDF files.
- Divide extracted text into smaller, manageable chunks.
- Generate vector embeddings for the text chunks.
- Store and retrieve relevant information using FAISS.
- Generate answers using Google's Gemini API.
- Support follow-up questions using conversation history.

## 3. Features

- **PDF Upload:** Upload PDF documents through a simple web interface.
- **Text Extraction:** Extract readable text from uploaded PDF files.
- **Text Chunking:** Divide extracted text into smaller chunks for efficient retrieval.
- **Embedding Generation:** Convert text chunks into numerical vector representations.
- **Vector Search:** Use FAISS to find relevant chunks based on user queries.
- **AI-Powered Answers:** Generate context-aware responses using Google's Gemini API.
- **Chat History:** Maintain recent conversation history to understand follow-up questions.
- **Document Preview:** Display extracted text after successful PDF processing.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Frontend interactions |
| Google Gemini API | AI-based answer generation |
| FAISS | Vector similarity search |
| Sentence Transformers | Text embedding generation |
| PyPDF | PDF text extraction |
| Python-Dotenv | Environment variable management |

## 5. Project Architecture

The application follows a Retrieval-Augmented Generation (RAG) architecture.

### Workflow

1. User uploads a PDF document.
2. The backend extracts text from the PDF.
3. Extracted text is divided into smaller chunks.
4. An embedding model converts the chunks into vector embeddings.
5. The embeddings and corresponding text chunks are stored in FAISS.
6. User submits a question through the chatbot interface.
7. The question is converted into an embedding.
8. FAISS retrieves the most relevant text chunks.
9. Retrieved chunks are passed to the Gemini API along with the user's question.
10. Gemini generates an answer based on the retrieved PDF content.
11. The answer is displayed in the chatbot interface.

## 6. Project Folder Structure

```text
AI-PDF-Chatbot/
│
├── backend/
│   └── rag_pipeline.py
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
├── uploads/
│
├── web/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │
│   └── templates/
│       └── index.html
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

*Note: The folder structure above represents the main project components. Additional files and folders may be present in your implementation.*

## 7. Installation and Setup

### Prerequisites

Make sure the following are installed:

- Python 3.10 or later
- pip (Python package manager)
- Git
- Google Gemini API key

### Step 1: Clone the Repository

```bash
git clone <your-github-repository-url>
```

Navigate into the project directory:

```bash
cd AI-PDF-Chatbot
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

You can obtain an API key from Google AI Studio:

https://aistudio.google.com/apikey

Keep your API key private. Never upload your `.env` file to GitHub.

### Step 5: Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000/
```

## 8. How to Use the Application

1. Open the application in your browser.
2. Select a PDF document from your computer.
3. Click the upload button.
4. Wait until the PDF is successfully processed.
5. Navigate to the chat section.
6. Enter a question related to the uploaded PDF.
7. Click Send.
8. View the AI-generated response.
9. Continue asking follow-up questions about the document.

## 9. Core Components

### PDF Processing

The PDF loader extracts readable text from uploaded documents. The extracted text is passed to the text splitter.

### Text Splitting

The text splitter divides the extracted document into smaller chunks. This makes information retrieval more efficient.

### Embedding Generation

The embedding module converts text chunks into numerical vectors using a sentence embedding model.

### Vector Storage and Retrieval

FAISS stores the generated embeddings and performs similarity searches to retrieve the most relevant chunks for a given question.

### RAG Pipeline

The RAG pipeline connects PDF processing, text splitting, embedding generation, vector retrieval, and AI-based answer generation.

### Gemini Integration

The Gemini API receives the retrieved document context and the user's question. It generates an answer using the provided context.

## 10. Retrieval-Augmented Generation (RAG)

RAG combines information retrieval with generative AI.

It consists of two major stages:

**1. Retrieval**

The system searches the vector database and identifies document chunks that are semantically similar to the user's question.

**2. Generation**

The retrieved information is provided to the language model, which generates a response based on the available document context.

This approach helps the chatbot answer questions using information from the uploaded PDF rather than relying entirely on its pre-trained knowledge.

## 11. Error Handling

The application handles common errors, including:

- Missing PDF files.
- Unsupported or unreadable PDF content.
- Empty extracted text.
- Missing API keys.
- Empty user questions.
- Vector retrieval failures.
- Gemini API errors.

## 12. Future Enhancements

- Support multiple PDF uploads.
- Allow users to chat with multiple documents simultaneously.
- Maintain chat sessions across application restarts.
- Display page references for generated answers.
- Support additional document formats such as DOCX and TXT.
- Improve response accuracy through optimized chunking and retrieval.
- Add user authentication and document management.

## 13. Conclusion

AI PDF Chatbot demonstrates how Retrieval-Augmented Generation can be used to build an intelligent document question-answering system.

By integrating PDF processing, text embeddings, FAISS vector search, and Google's Gemini API, the application enables users to interact with documents through natural language questions.

The project provides practical experience in Python development, Flask, Natural Language Processing, vector databases, and Generative AI.

---

**Developed using:** Python, Flask, FAISS, Sentence Transformers, and Google Gemini API.