# Text2SQL Cloud Cost Engine

This project is a Text-to-SQL system that allows a user to ask natural language questions about mock AWS and Azure billing data. It uses a semantic metadata layer to provide expert context to an LLM, enabling it to generate accurate SQLite queries.

The project is served in two parts:
1.  **FastAPI Backend:** A robust API that handles all the logic (as required by the assignment).
2.  **Streamlit Chat UI:** A user-friendly, conversational frontend that communicates with the FastAPI backend.

## How to Run This Project

### 1. Clone the Repository
Clone this repository to your local machine.

### 2. Install Requirements
Create a virtual environment and install all the necessary Python packages.

```bash
# Create a requirements.txt file with the contents from the next section
pip install -r requirements.txt