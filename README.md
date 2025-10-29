# 🧠 Text2SQL Cloud Cost Engine  

*A beginner-friendly AI project to query cloud cost data using natural language.*

---

## 📘 Overview

This project is an intelligent **Text-to-SQL engine** that lets you ask questions like:

> “What was my AWS EC2 cost last month?”

and get structured answers directly from mock **AWS** and **Azure billing data**.

It uses:

- **FastAPI** for the backend (handles AI + SQL logic)  
- **Streamlit** for the chat interface  
- **SQLite** for the database  
- **LLM (Language Model)** to convert your questions into SQL queries  
- **Semantic Metadata Layer** to guide the model with expert cloud cost context  

---

## 🏗️ Project Architecture

<img width="1529" height="826" alt="Architecture Diagram" src="https://github.com/user-attachments/assets/5f010539-4ce1-42a0-a62f-b7f34592845a" />

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| AI Engine | OpenAI / LLM via LangChain |
| Metadata Profiling | Pandas Profiling / YData |
| Deployment | Localhost |

---

## 🚀 How to Run This Project (Step-by-Step for Beginners)

### 🪜 1. Clone the Repository

First, copy the project code to your computer.

```bash
git clone https://github.com/Cheth-code/Text_sql_Ai-Cloud-Billing.git
cd Text_sql_Ai-Cloud-Billing
````
### 🧱 2. Create and Activate a Virtual Environment
🐧 On Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
````
🪟 On Windows:
```bash
python -m venv venv
venv\Scripts\activate
````
### 📦 3. Install Dependencies
This installs all the required Python libraries listed in requirements.txt.
```bash
pip install -r requirements.txt
````
### ⚙️ 4. Run the Backend (FastAPI)
This launches the backend API, which processes questions and returns SQL results.

Option 1 (simpler alternative):
```bash
python -m app
````
Option 2 (If you have uv installed on your machine):
```bash
uvicorn app:app --reload
````
Once it’s running, you should see something like:
```bash
Application running on http://127.0.0.1:8000
````
### 💬 5. Run the Frontend (Streamlit)
This starts the chat-style user interface that talks to the FastAPI backend.
```bash
streamlit run chat_app.py
````
Now, open your browser and go to:
```bash
http://localhost:8501
````
🎉 You can now chat with your AI assistant about your cloud costs!
###🧩 Example Queries

Try asking:

1.“Show me the total AWS cost for EC2.”

2.“Compare Azure and AWS storage spending.”

3.“What was the highest billing service last month?”

###🧠 How It Works (Simplified)

1.You ask a natural language question.

2.The system uses LangChain + metadata to translate it into an accurate SQL query.

3.The FastAPI backend runs the query on a SQLite database.

4.The Streamlit UI displays the result in a clean, conversational format.
