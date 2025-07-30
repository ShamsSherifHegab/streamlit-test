import streamlit as st
import json
import requests
import uuid

# Try to load secrets from st.secrets (Streamlit Cloud), else fallback to os.environ (local dev)
if "ALLOWED_USERS" in st.secrets:
    allowed_users = st.secrets["ALLOWED_USERS"].split(",")
    token_key = st.secrets["TOKEN_KEY"]
    api_key = st.secrets["API_KEY"]
    client_secret_dict = {"web": dict(st.secrets["CLIENT_SECRET_WEB"])}
else:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    allowed_users = os.getenv("ALLOWED_USERS", "").split(",")
    token_key = os.getenv("TOKEN_KEY", "changeme")
    api_key = os.getenv("API_KEY", "")
    client_secret_json = os.getenv("CLIENT_SECRET_JSON", None)
    client_secret_dict = json.loads(client_secret_json) if client_secret_json else None

from auth.authenticate import Authenticator

REDIRECT_URI = "https://app-test-ngonccnz6xxt2cfap2qptn.streamlit.app"

st.title("Initiate Qualification Call")

authenticator = Authenticator(
    allowed_users=allowed_users,
    token_key=token_key,
    secret_path=None,  # Not used when client_secret_dict is provided
    client_secret_dict=client_secret_dict,
    redirect_uri=REDIRECT_URI,
)
authenticator.check_auth()
authenticator.login()

if st.session_state.get("connected"):
    st.write(f"Welcome! {st.session_state['user_info'].get('email')}")
    st.markdown("**Example phone number:** `+971502337602`")
    phone_number = st.text_input("Enter phone number:")
    if st.button("Send POST Request"):
        generated_id = str(uuid.uuid4())
        url = "https://ai-control-service.staging.huspy.net/v1/leads/qualifications/rebu/initiate-call"
        headers = {
            "X-Service": "salesforce",
            "Content-Type": "application/json",
            "X-API-KEY": api_key,
        }
        payload = {
            "id": generated_id,
            "phoneNumber": phone_number,
            "businessIdentifier": "AE_HUSPY",
            "language": "en",
            "snapshot": {
                "propertyPrice": "3000000",
                "propertyLocation": "Downtown dubai",
                "numberOfBedrooms": "3",
                "agentName": "Nathan",
                "status": "Pool",
                "inquiryDate":"20/05/2025"
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            st.write("Response status:", response.status_code)
            st.write("Response:", response.json())
        except Exception as e:
            st.error(f"Request failed: {e}")
    if st.button("Log out"):
        authenticator.logout()
else:
    st.info("Please log in with Google to use the app.") 