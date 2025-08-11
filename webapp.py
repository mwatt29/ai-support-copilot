import streamlit as st
import requests

# --- Configuration ---
API_BASE_URL = "http://localhost:8000" # Your FastAPI backend URL

# --- Page Layout ---
st.set_page_config(page_title="AI Support Copilot", layout="wide")
st.title("🤖 AI Support Copilot")

st.write("Create a temporary ticket to get an AI-powered suggestion.")
st.info("This interface calls the same FastAPI backend as the Zendesk app would.")

# --- Input Form ---
with st.form("ticket_form"):
    subject = st.text_input("Ticket Subject", "Can't reset password")
    body = st.text_area("Ticket Body", "I forgot my password and 2FA is blocking me.")
    
    submitted = st.form_submit_button("Get Suggestion")

# --- API Call and Display ---
if submitted:
    with st.spinner("Thinking..."):
        try:
            # 1. Create the ticket
            create_response = requests.post(
                f"{API_BASE_URL}/create_simple_ticket", # Assumes a new endpoint
                json={"subject": subject, "body": body, "org": "Acme Inc"}
            )
            create_response.raise_for_status()
            ticket_id = create_response.json().get("ticketId")

            if not ticket_id:
                st.error("Failed to get a valid ticket ID from the backend.")
            else:
                # 2. Get the suggestion
                suggest_response = requests.post(
                    f"{API_BASE_URL}/suggest",
                    json={"ticketId": ticket_id}
                )
                suggest_response.raise_for_status()
                data = suggest_response.json()

                # 3. Display the results
                st.success("Suggestion received!")
                st.subheader("Suggested Answer")
                st.markdown(data.get("answer", "No answer provided."))
                
                st.subheader("Sources Used")
                for source in data.get("sources", []):
                    with st.expander(source.get("title")):
                        st.text(source.get("snippet"))

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the backend API: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")