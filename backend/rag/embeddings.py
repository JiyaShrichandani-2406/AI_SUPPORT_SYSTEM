from sentence_transformers import SentenceTransformer

from .chunker import create_chunks


# ==========================================================
# EMBEDDING MODEL
# ==========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# ==========================================================
# CREATE EMBEDDINGS
# ==========================================================

def create_embeddings():

    print("\nLoading knowledge base chunks...")

    chunks = create_chunks()

    print(
        "Total chunks found:",
        len(chunks)
    )

    if not chunks:

        print("No chunks found.")

        return [], []


    # Extract text from chunks
    texts = [
        chunk["content"]
        for chunk in chunks
    ]


    print("\nCreating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )


    print("Embeddings created successfully.")

    return chunks, embeddings


# ==========================================================
# TEST EMBEDDINGS
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("KNOWLEDGE BASE EMBEDDINGS")
    print("==========================================")

    print(
        "Embedding Model:",
        MODEL_NAME
    )


    chunks, embeddings = create_embeddings()


    if len(chunks) > 0:

        print("\n==========================================")
        print("EMBEDDING RESULT")
        print("==========================================")


        print(
            "Total Chunks:",
            len(chunks)
        )


        print(
            "Total Embeddings:",
            len(embeddings)
        )


        print(
            "Embedding Dimensions:",
            len(embeddings[0])
        )


        print("\nFirst Chunk:")

        print(
            chunks[0]["content"][:300]
        )


        print("\nFirst Embedding:")

        print(
            embeddings[0]
        )


    else:

        print("\nNo embeddings were created.")