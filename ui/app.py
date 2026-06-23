import ast
import json

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Chat App",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("AI Chat App")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_text" not in st.session_state:
    st.session_state.document_text = ""


def create_conversation():
    response = requests.post(f"{API_BASE_URL}/conversation/")
    response.raise_for_status()
    return response.json()["conversation_id"]


def clean_agent_response(agent_response):
    if isinstance(agent_response, str):
        try:
            return json.loads(agent_response)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(agent_response)
            except Exception:
                return agent_response

    return agent_response


def render_message(content):
    content = clean_agent_response(content)

    if isinstance(content, dict):
        text = content.get("text", "")

        text = clean_agent_response(text)

        while isinstance(text, dict):
            text = text.get("text", "")

            if isinstance(text, str):
                text = clean_agent_response(text)

        if text:
            st.write(text)

        file_url = content.get("file_url")
        if file_url:
            print("GRAPH URL:", file_url)
            st.image(file_url, use_container_width=True)

    else:
        st.write(content)


if st.button("New Conversation"):
    st.session_state.conversation_id = create_conversation()
    st.session_state.messages = []
    st.session_state.document_text = ""
    st.success(f"Conversation created: {st.session_state.conversation_id}")

if st.session_state.conversation_id:
    st.caption(f"Conversation ID: {st.session_state.conversation_id}")
else:
    st.warning("Click 'New Conversation' before chatting.")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message["content"])


with st.sidebar:
    st.header("File Upload")

    uploaded_file = st.file_uploader(
        "Upload File",
        type=["csv", "pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        if st.button("Upload"):
            filename = uploaded_file.name.lower()

            if filename.endswith(".csv"):
                endpoint = "/chat/upload_csv"
                upload_type = "CSV"

            elif filename.endswith(".pdf"):
                endpoint = "/chat/upload_pdf"
                upload_type = "PDF"

            elif filename.endswith((".png", ".jpg", ".jpeg")):
                endpoint = "/chat/upload_image"
                upload_type = "Image"

            else:
                endpoint = None
                upload_type = None
                st.error("Unsupported file type.")

            if endpoint:
                with st.spinner(f"Uploading {upload_type}..."):
                    response = requests.post(
                        f"{API_BASE_URL}{endpoint}",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type
                            )
                        }
                    )

                if response.status_code == 200:
                    result = response.json()

                    st.session_state.document_text = result.get(
                        "extracted_text",
                        st.session_state.document_text
                    )

                    rows_inserted = result.get("rows_inserted", 0)
                    rows_skipped = result.get("rows_skipped", 0)

                    st.success(
                        f"{upload_type} uploaded successfully. "
                        f"Rows inserted: {rows_inserted}, skipped: {rows_skipped}"
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": {
                            "text": (
                                f"{upload_type} uploaded successfully.\n\n"
                                f"Rows Inserted: {rows_inserted}\n"
                                f"Rows Skipped: {rows_skipped}"
                            )
                        }
                    })

                    st.rerun()

                else:
                    st.error(f"{upload_type} upload failed.")
                    st.write(response.text)


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

        is_graph_request = any(
            word in user_input.lower()
            for word in ["graph", "chart", "plot", "bar", "pie"]
        )

        st.write("Graph request:", is_graph_request)

        form_data = {
            "message": user_input,
            "conversation_id": st.session_state.conversation_id,
            "document_text": st.session_state.document_text
        }

        if is_graph_request:

            api_response = requests.post(
                f"{API_BASE_URL}/chat/",
                data=form_data
            )

            if api_response.status_code == 200:
                result_json = api_response.json()
                st.write("DEBUG RESPONSE")
                st.json(result_json)

                agent_response = result_json["agent_response"]

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_response
                })

                with st.chat_message("assistant"):
                    render_message(agent_response)

        else:

            with st.chat_message("assistant"):

                response_placeholder = st.empty()
                streamed_text = ""

                with requests.post(
                        f"{API_BASE_URL}/chat/stream",
                        data=form_data,
                        stream=True
                ) as response:

                    for chunk in response.iter_content(
                            chunk_size=None,
                            decode_unicode=True
                    ):
                        if chunk:
                            streamed_text += chunk
                            response_placeholder.markdown(streamed_text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": {
                        "text": streamed_text,
                        "file_url": None
                    }
                })
