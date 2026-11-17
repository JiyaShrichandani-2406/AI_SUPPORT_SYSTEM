# AI Technical Support System

An AI-powered technical support platform that automates customer support ticket management using Gmail integration, Artificial Intelligence, and Retrieval-Augmented Generation (RAG).

## 1. Project Overview

The **AI Technical Support System** is designed to simplify and automate technical support operations.

The system retrieves customer support emails from Gmail, converts relevant emails into support tickets, analyzes tickets using AI, identifies their priority and category, and generates context-aware technical responses using a knowledge base.

It provides a frontend dashboard for viewing and managing support tickets and a Python FastAPI backend for processing requests.

## 2. Project Objectives

- Automate the collection of customer support emails.
- Convert customer emails into structured support tickets.
- Analyze technical issues using AI.
- Classify tickets based on their category and priority.
- Generate relevant solutions using a knowledge base.
- Reduce manual effort in customer support operations.
- Support ticket approval and customer email responses.

## 3. Key Features

### Gmail Integration
- Connects to Gmail using Google OAuth authentication.
- Retrieves customer support emails.
- Filters irrelevant emails, such as security notifications and delivery failure messages.
- Prevents duplicate email processing.

### Automated Ticket Creation
- Converts eligible customer emails into support tickets.
- Extracts ticket information, including subject, sender, and message.
- Assigns a unique ticket ID.

### AI-Based Ticket Analysis
- Analyzes incoming technical issues.
- Identifies ticket categories and priority.
- Helps support teams understand and organize customer issues.

### RAG-Based Response Generation
- Uses Retrieval-Augmented Generation (RAG).
- Retrieves relevant information from the technical support knowledge base.
- Generates context-aware responses using the retrieved information and an Ollama language model.

### Ticket Management
- Displays support tickets through the frontend dashboard.
- Allows users to view ticket details.
- Supports ticket status management.

### Customer Email Response
- Sends approved responses to the respective customer through Gmail.
- Uses the sender information associated with the selected ticket.

## 4. Technologies Used

| Component | Technology |
|---|---|
| Backend | Python |
| Backend Framework | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLAlchemy with configured database |
| AI Model | Ollama – Llama 3.2 |
| Embedding Model | Sentence Transformers – all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Retrieval Technique | RAG |
| Email Integration | Gmail API |
| Authentication | Google OAuth 2.0 |
| API Server | Uvicorn |

## 5. Project Structure

```text
AI_SUPPORT_SYSTEM/
│
├── backend/
│   ├── ai_module/
│   ├── database/
│   ├── rag/
│   ├── main.py
│   ├── email_reader.py
│   ├── email_sender.py
│   └── models.py
│
├── frontend/
│   └── Frontend application files
│
├── knowledge_base/
│   └── Technical support knowledge files
│
├── chroma_db/
│   └── Vector database storage
│
├── venv/
│   └── Python virtual environment
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env (if configured)
```

*Note: This is a simplified project structure. Actual files and folders may vary.*

## 6. Prerequisites

Before running the project, install:

1. Python
2. Visual Studio Code
3. Git
4. Ollama
5. Node.js only if required by the frontend setup
6. A Google Cloud project with Gmail API enabled

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd AI_SUPPORT_SYSTEM
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Ollama

Install Ollama and download the required language model:

```bash
ollama pull llama3.2:latest
```

Make sure Ollama is running before testing AI response generation.

### Step 6: Configure Gmail API

1. Enable the Gmail API in Google Cloud Console.
2. Configure OAuth consent and authentication.
3. Download the OAuth client credentials file.
4. Place `credentials.json` in the project root if required by the application.
5. Run the Gmail integration to complete authorization and generate the token file.

**Important:** Never upload `credentials.json`, `token.json`, or other private credentials to GitHub.

## 8. How to Run the Project

### Step 1: Start the Backend

Open the project in Visual Studio Code.

Open a terminal and execute:

```powershell
cd AI_SUPPORT_SYSTEM
.\venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --reload
```

The backend will start at:

```text
http://127.0.0.1:8000
```

### Step 2: Verify Backend

Open the following URL in your browser:

```text
http://127.0.0.1:8000
```

To explore the available API endpoints, open:

```text
http://127.0.0.1:8000/docs
```

### Step 3: Run Gmail Email Reader

Open another VS Code terminal:

```powershell
cd AI_SUPPORT_SYSTEM
.\venv\Scripts\Activate.ps1
cd backend
python email_reader.py
```

The email reader connects to Gmail, retrieves eligible customer emails, and sends them to the backend for ticket processing.

### Step 4: Start the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Start the frontend using its configured development method.

For example, if the frontend uses Vite:

```bash
npm install
npm run dev
```

If it uses plain HTML, CSS, and JavaScript, open the existing HTML file using VS Code Live Server.

Open the frontend URL displayed by your development server.

## 9. System Workflow

1. Customer sends a technical support email.
2. Gmail API retrieves the email.
3. The email reader filters irrelevant and duplicate messages.
4. The backend processes the email and creates a support ticket.
5. AI analyzes the ticket and identifies its category and priority.
6. RAG retrieves relevant technical information from the knowledge base.
7. The language model generates a context-aware response.
8. The frontend displays the ticket and its analysis.
9. An authorized support user can review and approve the response.
10. The approved response is sent to the customer through Gmail.

## 10. API Documentation

The FastAPI backend provides API documentation through Swagger UI.

```text
http://127.0.0.1:8000/docs
```

This interface can be used to explore and test the available API endpoints.

## 11. Security Considerations

- Gmail authentication uses OAuth 2.0.
- Private credentials should not be committed to GitHub.
- The virtual environment should not be uploaded.
- Customer email content should be handled securely.
- Test data should be used when demonstrating the project.

## 12. Future Enhancements

- User authentication and role-based access.
- Advanced ticket analytics and reporting.
- Improved AI response accuracy.
- Ticket assignment and escalation.
- Additional email integrations.
- Enhanced dashboard and notification features.

## 13. Conclusion

The AI Technical Support System combines email automation, Artificial Intelligence, and Retrieval-Augmented Generation to improve technical support operations.

It aims to reduce manual ticket handling, assist support teams in analyzing customer issues, and generate relevant technical responses through an integrated frontend and backend architecture.

---

