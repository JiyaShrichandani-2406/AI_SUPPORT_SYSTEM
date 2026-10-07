from pathlib import Path
import chromadb

from .embeddings import create_embeddings


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CHROMA_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "technical_support_knowledge"


# ==========================================================
# CHROMADB CLIENT
# ==========================================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# ==========================================================
# COLLECTION
# ==========================================================

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ==========================================================
# STORE EMBEDDINGS
# ==========================================================

def store_embeddings():

    print("\nLoading chunks and creating embeddings...")

    chunks, embeddings = create_embeddings()

    if not chunks:

        print("No chunks found.")

        return


    ids = []

    documents = []

    metadatas = []


    for chunk in chunks:

        ids.append(
            chunk["chunk_id"]
        )

        documents.append(
            chunk["content"]
        )

        metadatas.append({

            "source": chunk["source"],

            "file_name": chunk["file_name"],

            "category": chunk["category"]

        })


    print("\nStoring data in ChromaDB...")


    collection.upsert(

        ids=ids,

        documents=documents,

        embeddings=embeddings.tolist(),

        metadatas=metadatas

    )


    print("\n==========================================")
    print("CHROMADB STORAGE")
    print("==========================================")

    print(
        "Collection:",
        COLLECTION_NAME
    )

    print(
        "Documents stored:",
        len(chunks)
    )

    print(
        "Database location:",
        CHROMA_PATH
    )


# ==========================================================
# VERIFY DATABASE
# ==========================================================

def verify_database():

    print("\n==========================================")
    print("CHROMADB VERIFICATION")
    print("==========================================")

    total_documents = collection.count()

    print(
        "Total documents in ChromaDB:",
        total_documents
    )


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    store_embeddings()

    verify_database()