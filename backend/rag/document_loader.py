from pathlib import Path


# ==========================================================
# KNOWLEDGE BASE LOCATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"


# ==========================================================
# LOAD MARKDOWN DOCUMENTS
# ==========================================================

def load_documents():

    documents = []

    # Check whether knowledge_base exists
    if not KNOWLEDGE_BASE_DIR.exists():

        print("Knowledge base folder not found.")

        return documents


    # Find all Markdown files
    markdown_files = KNOWLEDGE_BASE_DIR.rglob("*.md")


    for file_path in markdown_files:

        try:

            # Read file
            content = file_path.read_text(
                encoding="utf-8"
            )


            # Category = parent folder
            category = file_path.parent.name


            # File name
            file_name = file_path.name


            # Store document
            document = {

                "content": content,

                "source": str(
                    file_path.relative_to(
                        KNOWLEDGE_BASE_DIR
                    )
                ),

                "file_name": file_name,

                "category": category
            }


            documents.append(document)


        except Exception as error:

            print(
                f"Error reading {file_path}: {error}"
            )


    return documents


# ==========================================================
# TEST LOADER
# ==========================================================

if __name__ == "__main__":

    documents = load_documents()


    print("\n==========================================")
    print("KNOWLEDGE BASE DOCUMENT LOADER")
    print("==========================================")

    print(
        f"Knowledge Base: {KNOWLEDGE_BASE_DIR}"
    )

    print(
        f"Documents Loaded: {len(documents)}"
    )


    for document in documents:

        print("\n------------------------------------------")

        print(
            "File:",
            document["file_name"]
        )

        print(
            "Category:",
            document["category"]
        )

        print(
            "Source:",
            document["source"]
        )

        print(
            "Characters:",
            len(document["content"])
        )