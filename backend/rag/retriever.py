from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CHROMA_PATH = BASE_DIR / "chroma_db"


# ==========================================================
# CHROMADB CONFIGURATION
# ==========================================================

COLLECTION_NAME = "technical_support_knowledge"


client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


collection = client.get_collection(
    name=COLLECTION_NAME
)


# ==========================================================
# EMBEDDING MODEL
# ==========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME
)


# ==========================================================
# RETRIEVE RELEVANT KNOWLEDGE
# ==========================================================

def retrieve_knowledge(
    query,
    top_k=3
):

    print("\n==========================================")
    print("KNOWLEDGE RETRIEVAL")
    print("==========================================")

    print(
        "Query:",
        query
    )


    # ------------------------------------------------------
    # Convert query into embedding
    # ------------------------------------------------------

    query_embedding = model.encode(
        [query]
    )


    # ------------------------------------------------------
    # Search ChromaDB
    # ------------------------------------------------------

    results = collection.query(

        query_embeddings=query_embedding.tolist(),

        n_results=top_k

    )


    return results


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

def display_results(results):

    print("\n==========================================")
    print("RETRIEVED KNOWLEDGE")
    print("==========================================")


    documents = results.get(
        "documents",
        [[]]
    )[0]


    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    distances = results.get(
        "distances",
        [[]]
    )[0]


    if not documents:

        print("No relevant documents found.")

        return


    for index, document in enumerate(documents):

        print(
            f"\n--- Result {index + 1} ---"
        )


        print(
            "Source:",
            metadatas[index].get(
                "source",
                "Unknown"
            )
        )


        print(
            "Category:",
            metadatas[index].get(
                "category",
                "Unknown"
            )
        )


        print(
            "Distance:",
            distances[index]
        )


        print("\nContent:")

        print(
            document[:1000]
        )


# ==========================================================
# TEST RETRIEVER
# ==========================================================

if __name__ == "__main__":

    test_query = (
        "Customer payment is failing "
        "and the transaction is being declined."
    )


    results = retrieve_knowledge(
        test_query,
        top_k=3
    )


    display_results(
        results
    )