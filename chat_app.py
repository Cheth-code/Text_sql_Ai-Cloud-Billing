import streamlit as st
import requests
import json

# Set the title for your app
st.title("Cloud Cost AI Chat 💬")
st.write("I can answer questions about your AWS and Azure cloud costs. Try me!")

# --- Configuration ---
FASTAPI_URL = "http://127.0.0.1:8000/query"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the assistant message has details, show them
        if "details" in message:
            with st.expander("Show technical details"):
                st.write(f"**Selected Table:** `{message['details']['table']}`")
                st.code(message['details']['sql'], language="sql")
                st.dataframe(message['details']['data'])


# Function to call the FastAPI backend
def get_sql_answer(question):
    try:
        response = requests.post(FASTAPI_URL, json={"question": question})
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Backend not running. Please start the FastAPI app first!"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}

# React to user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = get_sql_answer(prompt)
            
            if "error" in response_data:
                st.error(response_data["error"])
                # Add error to session state
                st.session_state.messages.append({"role": "assistant", "content": response_data["error"]})
            else:
                answer = response_data.get("descriptive_answer", "Sorry, I couldn't find an answer.")
                
                # Prepare the technical details
                details = {
                    "table": response_data.get("selected_table"),
                    "sql": response_data.get("sql_query"),
                    "data": response_data.get("query_result", "[]") # Parse data for dataframe
                }
                
                # Display the answer
                st.markdown(answer)
                with st.expander("Show technical details"):
                    st.write(f"**Selected Table:** `{details['table']}`")
                    st.code(details['sql'], language="sql")
                    st.dataframe(details['data'])
                
                # Add assistant response and details to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "details": details
                })