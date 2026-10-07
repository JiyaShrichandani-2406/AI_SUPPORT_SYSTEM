import json

from langchain_ollama import OllamaLLM


# ==========================================
# CONNECT TO OLLAMA
# ==========================================

llm = OllamaLLM(
    model="llama3.2"
)


# ==========================================
# AI TRIAGE FUNCTION
# ==========================================

def analyze_ticket(subject: str, message: str):

    prompt = f"""
You are an AI technical support assistant.

Analyze the following support ticket.

Subject:
{subject}

Message:
{message}

Return ONLY a valid JSON object.

Use exactly these fields:

{{
    "summary": "short summary of the problem",
    "category": "technical category",
    "intent": "customer intent",
    "urgency": "Low, Medium, or High",
    "sentiment": "Positive, Neutral, or Negative",
    "key_details": []
}}

IMPORTANT RULES:

1. Return ONLY valid JSON.

2. Do NOT use Markdown.

3. Do NOT use ```json.

4. Do NOT add explanations before or after the JSON.

5. Use ONLY information explicitly provided in the ticket.

6. Do NOT invent technical facts.

7. Do NOT claim that you checked any internal system.

8. Extract all important technical details explicitly
   mentioned in the ticket.

9. Extract details such as:
   - Server names
   - IP addresses
   - Port numbers
   - Error codes
   - Log IDs
   - Case IDs
   - Ticket IDs
   - Configuration values
   - Timestamps
   - Database names
   - Application names
   - Other technical identifiers

10. Put these details inside the key_details array.

11. Do NOT create a missing_information field.

12. key_details must always be a JSON array.

13. Determine urgency only from information provided
    in the ticket.

14. Determine sentiment only from the customer's
    wording and tone.

15. Make sure the JSON is complete.
"""

    print("\nSending ticket to AI...\n")

    response = llm.invoke(prompt)

    response = response.strip()

    # Remove Markdown code fences if present
    if response.startswith("```json"):
        response = response[7:]

    elif response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    # Convert AI response to Python dictionary
    try:

        ai_result = json.loads(response)

        return ai_result

    except json.JSONDecodeError as error:

        print("AI returned invalid JSON.")
        print("Error:", error)
        print("Raw response:", response)

        return None