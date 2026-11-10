
from sentence_transformers import CrossEncoder

class DocumentReranker:

    def __init__(self):
        print("Loading Cross-Encoder model...")

        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L6-v2"
        )

        print("Cross-Encoder loaded successfully!")

    def rerank(self, question, chunks, top_k=3):

        if not chunks:
            return []

        pairs = [
            [question, chunk]
            for chunk in chunks
        ]

        scores = self.model.predict(pairs)

        ranked_chunks = sorted(
            zip(chunks, scores),
            key=lambda item: item[1],
            reverse=True
        )

        return [
            chunk
            for chunk, score in ranked_chunks[:top_k]
        ]
