import requests

from .retriever import retrieve_knowledge


# ==========================================================
# OLLAMA CONFIGURATION
# ==========================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"

# Give Ollama enough time, but don't allow extremely long runs
OLLAMA_TIMEOUT = 180

# Keep generation small and fast
MAX_OUTPUT_TOKENS = 80
CONTEXT_SIZE = 1024

DEFAULT_TOP_K = 2

# Limit retrieved knowledge sent to the model
MAX_KNOWLEDGE_CHARS = 1800


# ==========================================================
# BUILD KNOWLEDGE CONTEXT
# ==========================================================

def build_knowledge_context(documents):

    if not documents:
        return ""

    context_parts = []

    for index, document in enumerate(documents, start=1):

        if not document:
            continue

        context_parts.append(
            f"Knowledge {index}:\n{document}"
        )

    context = "\n\n".join(context_parts)

    if len(context) > MAX_KNOWLEDGE_CHARS:
        context = context[:MAX_KNOWLEDGE_CHARS]

    return context


# ==========================================================
# CLEAN RESPONSE
# ==========================================================

def clean_response(response):

    if not response:
        return ""

    response = response.strip()

    response = response.replace("```text", "")
    response = response.replace("```", "")

    return response.strip()


# ==========================================================
# GENERATE RAG RESPONSE
# ==========================================================

def generate_rag_response(ticket_text, top_k=DEFAULT_TOP_K):

    if not ticket_text:
        return {
            "response": "",
            "sources": []
        }

    # ======================================================
    # STEP 1 — RETRIEVE KNOWLEDGE
    # ======================================================

    print("\n==========================================")
    print("KNOWLEDGE RETRIEVAL")
    print("==========================================")

    print("Searching knowledge base...")

    try:

        results = retrieve_knowledge(
            ticket_text,
            top_k=top_k
        )

    except Exception as error:

        print("\nKnowledge retrieval error:")
        print(error)

        return {
            "response": "",
            "sources": []
        }

    # ======================================================
    # STEP 2 — EXTRACT DOCUMENTS
    # ======================================================

    documents = results.get(
        "documents",
        []
    )

    metadatas = results.get(
        "metadatas",
        []
    )

    if documents:
        documents = documents[0]
    else:
        documents = []

    if metadatas:
        metadatas = metadatas[0]
    else:
        metadatas = []

    # ======================================================
    # STEP 3 — CHECK KNOWLEDGE
    # ======================================================

    if not documents:

        print("\nNo relevant knowledge found.")

        fallback_response = (
            "Hello,\n\n"
            "Thank you for contacting our support team. "
            "Please provide the exact error message or any "
            "additional information shown during checkout "
            "so we can investigate the issue further.\n\n"
            "Regards,\n"
            "Technical Support Team"
        )

        return {
            "response": fallback_response,
            "sources": []
        }

    # ======================================================
    # STEP 4 — BUILD SMALL KNOWLEDGE CONTEXT
    # ======================================================

    knowledge_context = build_knowledge_context(
        documents
    )

    sources = []

    for index, metadata in enumerate(metadatas):

        if isinstance(metadata, dict):

            source = metadata.get(
                "source",
                "Unknown"
            )

            if source not in sources:
                sources.append(source)

    # ======================================================
    # DISPLAY RETRIEVED KNOWLEDGE
    # ======================================================

    print("\n==========================================")
    print("RETRIEVED KNOWLEDGE")
    print("==========================================")

    print(
        "Number of chunks:",
        len(documents)
    )

    print("\nSources:")

    for source in sources:
        print("-", source)

    print(
        "\nKnowledge context length:",
        len(knowledge_context),
        "characters"
    )

    # ======================================================
    # STEP 5 — SMALL CLIENT-FACING PROMPT
    # ======================================================

    prompt = f"""You are a technical support assistant.

Write a short professional email directly to the customer.

Use only the customer message and technical information provided below.

Do not invent error codes, causes, system checks, or troubleshooting results.

If the exact cause is unknown, say that it cannot yet be confirmed.

If information is missing, ask the customer for the specific information needed.

Do not mention AI, RAG, ChromaDB, Llama, embeddings, knowledge base, or internal documentation.

Do not claim the issue is fixed.

CUSTOMER TICKET:
{ticket_text}

TECHNICAL INFORMATION:
{knowledge_context}

Return ONLY the customer-facing email.

Start with:
Hello,
"""

    # ======================================================
    # STEP 6 — SEND TO OLLAMA
    # ======================================================

    print("\n==========================================")
    print("SENDING REQUEST TO OLLAMA")
    print("==========================================")

    print("Model:", OLLAMA_MODEL)
    print("Prompt characters:", len(prompt))
    print("Please wait...")

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "stream": False,

        "keep_alive": "5m",

        "options": {

            "num_predict": MAX_OUTPUT_TOKENS,

            "num_ctx": CONTEXT_SIZE,

            "temperature": 0.1
        }
    }

    try:

        response = requests.post(

            OLLAMA_URL,

            json=payload,

            timeout=OLLAMA_TIMEOUT
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:

        print(
            "\nOLLAMA ERROR:"
        )

        print(
            f"Request timed out after "
            f"{OLLAMA_TIMEOUT} seconds."
        )

        return {
            "response": "",
            "sources": sources
        }

    except requests.exceptions.ConnectionError:

        print("\nCould not connect to Ollama.")

        return {
            "response": "",
            "sources": sources
        }

    except requests.exceptions.RequestException as error:

        print("\nOllama request error:")
        print(error)

        return {
            "response": "",
            "sources": sources
        }

    # ======================================================
    # STEP 7 — PARSE RESPONSE
    # ======================================================

    try:

        result = response.json()

    except ValueError:

        print("\nInvalid JSON response from Ollama.")

        return {
            "response": "",
            "sources": sources
        }

    generated_response = clean_response(
        result.get("response", "")
    )

    # ======================================================
    # STEP 8 — CHECK RESPONSE
    # ======================================================

    if not generated_response:

        print("\nOllama returned an empty response.")

        return {
            "response": "",
            "sources": sources
        }

    # ======================================================
    # STEP 9 — ENSURE CLOSING
    # ======================================================

    if "Technical Support Team" not in generated_response:

        generated_response += (
            "\n\nRegards,\n"
            "Technical Support Team"
        )

    # ======================================================
    # STEP 10 — DISPLAY RESULT
    # ======================================================

    print("\n==========================================")
    print("CLIENT-READY RESPONSE")
    print("==========================================")

    print(generated_response)

    print("\n==========================================")
    print("SOURCES")
    print("==========================================")

    for source in sources:
        print("-", source)

    # ======================================================
    # STEP 11 — RETURN TO FASTAPI
    # ======================================================

    return {

        "response": generated_response,

        "sources": sources
    }


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == "__main__":

    test_ticket = """
Subject: Payment checkout issue

Customer Message:
I am trying to complete a payment, but the checkout is failing.

The checkout page loads correctly, but the payment is being declined.

I do not see any detailed error message.
"""

    result = generate_rag_response(
        ticket_text=test_ticket,
        top_k=2
    )

    print("\n==========================================")
    print("FINAL RESULT")
    print("==========================================")

    print("\nResponse:")
    print(result["response"])

    print("\nSources:")

    for source in result["sources"]:
        print("-", source)