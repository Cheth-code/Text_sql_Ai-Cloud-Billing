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
<img width="1784" height="1010" alt="text-to_sql" src="https://github.com/user-attachments/assets/3bc0400f-4624-4681-8394-8da56583fbd4" />
---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| AI Engine | OpenAI / LLM via LangChain |
| Deployment | Localhost |

---

## 🚀 How to Run This Project 


### 🪜 1. Clone the Repository

First, copy the project code to your computer.

```bash
git clone https://github.com/Cheth-code/Text_sql_Ai-Cloud-Billing.git
cd Text_sql_Ai-Cloud-Billing
````
### 🧱 2. Create and Activate a Virtual Environment

```bash
uv venv
.venv\Scripts\activate
````
### 📦 3. Install Dependencies
This installs all the required libraires
```bash
uv sync
````
### 📦 4. Create a .env file in Text_sql_Ai-Cloud-Billing
This would hold your openai_api_key, paste it 
```bash
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY" 
````
##  Now for the 3 Step-process to run this
Make sure the datasets are in util file
This loads the given_datasets.csv to sqlite database
got to util
```bash
cd util
````
run load_data.py
```bash
uv run load_data.py
````
cloud_costs.db gets created 

### NEXT Run the metadata_by_ai.py
This creates a sematic_metadata.json by analysing all the columns of the cloud_costs.db
with an AI description

run metadata_by_ai.py
```bash
uv run metadata_by_ai.py
````
sematic_metadata.json is created

### ⚙️ NOW Go back
```bash
cd ..
````

### ⚙️ NOW Run the Backend (FastAPI)
This launches the backend API, which processes questions and returns SQL results.

Run the app.py
```bash
uv run app.py
````

Once it’s running, you should see something like:
```bash
Application running on http://127.0.0.1:8000
````
### 💬 Run the Frontend (Streamlit)
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

### ❌ If you find these errors
```bash
INFO:     Started reloader process [58964] using StatReload
ERROR:    Error loading ASGI app. Attribute “app” not found in module “app”.
````
````
cloud_costs.db is created 
