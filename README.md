# Text2SQL Cloud Cost Engine

This project is a Text-to-SQL system that allows a user to ask natural language questions about mock AWS and Azure billing data. It uses a semantic metadata layer to provide expert context to an LLM, enabling it to generate accurate SQLite queries.

## Architecture of the project
<img width="1529" height="826" alt="diagram-export-27-10-2025-11_28_33" src="https://github.com/user-attachments/assets/5f010539-4ce1-42a0-a62f-b7f34592845a" />


The project is served in two parts:
1.  **FastAPI Backend:** A robust API that handles all the logic (as required by the assignment).
2.  **Streamlit Chat UI:** A user-friendly, conversational frontend that communicates with the FastAPI backend.

## How to Run This Project

```bash
# 1. Clone the repo
git clone https://github.com/Cheth-code/Text_sql_Ai-Cloud_Billing.git
cd Text_sql_Ai-Cloud_Billing

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # on Linux/macOS
venv\Scripts\activate          # on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run app.py file
python -m app
uvicorn app:app --reload
# running on http://localhost:8501

# 5. Now the frontend by using Streamlit
streamlit run chat_app.py
