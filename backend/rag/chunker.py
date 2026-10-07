from pathlib import Path

from .document_loader import load_documents


# ==========================================================
# CHUNK SETTINGS
# ==========================================================

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200


# ==========================================================
# CREATE CHUNKS
# ==========================================================

def create_chunks():

    documents = load_documents()

    all_chunks = []


    for document in documents:

        content = document["content"]

        source = document["source"]

        file_name = document["file_name"]

        category = document["category"]


        # --------------------------------------------------
        # Create a safe unique prefix
        # --------------------------------------------------

        safe_category = category.replace(
            " ",
            "_"
        )

        safe_file_name = Path(
            file_name
        ).stem.replace(
            " ",
            "_"
        )


        # --------------------------------------------------
        # Create chunks
        # --------------------------------------------------

        start = 0

        chunk_number = 0


        while start < len(content):

            end = start + CHUNK_SIZE

            chunk_content = content[start:end]


            # --------------------------------------------------
            # UNIQUE CHUNK ID
            # --------------------------------------------------

            chunk_id = (
                f"{safe_category}_"
                f"{safe_file_name}_"
                f"{chunk_number}"
            )


            all_chunks.append({

                "chunk_id": chunk_id,

                "content": chunk_content,

                "source": source,

                "file_name": file_name,

                "category": category

            })


            # --------------------------------------------------
            # Move to next chunk
            # --------------------------------------------------

            start += (
                CHUNK_SIZE -
                CHUNK_OVERLAP
            )

            chunk_number += 1


    print(
        "Total chunks created:",
        len(all_chunks)
    )


    return all_chunks


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    chunks = create_chunks()


    print("\n==========================================")
    print("CHUNKING RESULT")
    print("==========================================")


    print(
        "Total Chunks:",
        len(chunks)
    )


    if chunks:

        print("\nFirst 5 Chunk IDs:")


        for chunk in chunks[:5]:

            print(
                chunk["chunk_id"]
            )