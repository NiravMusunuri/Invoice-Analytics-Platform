import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Chat App",
    page_icon="🤖",
    layout="centered"
)

st.title("AI Chat App")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def create_conversation():
    api_response = requests.post(f"{API_BASE_URL}/conversation/")
    api_response.raise_for_status()

    result_json = api_response.json()
    return result_json["conversation_id"]


if st.button("New Conversation"):
    st.session_state.conversation_id = create_conversation()
    st.session_state.messages = []
    st.success(f"Conversation created: {st.session_state.conversation_id}")

if st.session_state.conversation_id:
    st.caption(f"Conversation ID: {st.session_state.conversation_id}")
else:
    st.warning("Click 'New Conversation' before chatting.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


with st.sidebar:
    st.header("File Upload")
    uploaded_file = st.file_uploader(
        "Upload a file",
        type=["txt", "csv", "pdf"]
    )

user_input = st.chat_input("Type your message...")

if user_input:
    if st.session_state.conversation_id is None:
        st.error("Please create a conversation first.")
    else:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

            if uploaded_file is not None:
                st.caption(f"📎 {uploaded_file.name}")

        form_data = {
            "message": user_input
        }

        files = None

        if uploaded_file is not None:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

        with st.spinner("Thinking..."):
            api_response = requests.post(
                f"{API_BASE_URL}/chat/",
                data=form_data,
                files=files
            )

        if api_response.status_code == 200:
            result_json = api_response.json()
            agent_response = result_json["agent_response"]

            st.session_state.messages.append({
                "role": "assistant",
                "content": agent_response
            })

            with st.chat_message("assistant"):
                st.write(agent_response)

        else:
            st.error("API request failed.")
            st.write(api_response.text)