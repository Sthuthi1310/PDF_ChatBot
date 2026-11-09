
from sentence_transformers import SentenceTransformer

# Load the embedding model
model = None

def load_embedding_model():
    global model

    if model is None:
        print("Loading embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded successfully!")

    return model


# Convert text chunks into numerical embeddings
def generate_embeddings(chunks):

    if not chunks:
        return []

    embedding_model = load_embedding_model()

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings
