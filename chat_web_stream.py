
import streamlit as st
import openai
import os

# Use st.secrets in the cloud, .env locally
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

# Page settings
st.set_page_config(page_title="GPT-4o Chat", layout="centered")
st.title("💬 GPT-4o Web Chat")

# Sidebar role selector
st.sidebar.header("⚙️ Settings")
role = st.sidebar.selectbox(
    "🧠 Choose GPT Role",
    [
        "Helpful Assistant",
        "Python Tutor",
        "Cher",
        "Historian",
        "Sarcastic Bot",
        "Real Estate Agent",
    ]
)

# Role to system prompt mapping
role_map = {
    "Helpful Assistant": "You are a helpful assistant.",
    "Python Tutor": "You are a kind and patient Python tutor who explains code step by step.",
    "Cher": "You are Cher, the singer and icon, answering questions with flair and sass.",
    "Historian": "You are a knowledgeable historian with a deep understanding of world history.",
    "Sarcastic Bot": "You are a sarcastic assistant who answers accurately but with dry wit.", 
    "Real Estate Agent": "You are a realtor with experience in the Washington, DC market.",
}

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📄 Upload a file", type=["txt", "pdf", "csv"])
uploaded_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        uploaded_text = uploaded_file.read().decode("utf-8")
        st.sidebar.success(f"Uploaded: {uploaded_file.name}")

    elif uploaded_file.type == "application/pdf":
        import fitz  # PyMuPDF
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            uploaded_text = "\n".join([page.get_text() for page in doc])
        st.sidebar.success(f"PDF extracted: {uploaded_file.name}")
        st.sidebar.write(uploaded_text[:500])  # 🧪 Show first 500 chars

    elif uploaded_file.type == "text/csv":
        import pandas as pd
        try:
            df = pd.read_csv(uploaded_file)
            uploaded_text = df.to_markdown(index=False)[:4000]  # Limit size for prompt
            st.sidebar.success(f"CSV loaded: {uploaded_file.name}")
            st.sidebar.write(df.head())  # Optional preview
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")


uploaded_text = ""
if uploaded_file is not None:
    uploaded_text = uploaded_file.read().decode("utf-8")
    st.sidebar.success("Text file uploaded!")


st.sidebar.markdown("---")

# New chat button
if st.sidebar.button("🧹 Start New Chat"):
    st.session_state.messages = [
        {"role": "system", "content": role_map[role]}
    ]
    st.session_state.active_role = role
    st.rerun()

# Download button
if "messages" in st.session_state and len(st.session_state.messages) > 1:
    chat_log_text = ""
    for msg in st.session_state.messages[1:]:
        chat_log_text += f"{msg['role'].capitalize()}: {msg['content']}\n\n"

    st.sidebar.download_button(
        label="💾 Download Chat Log",
        data=chat_log_text,
        file_name="gpt_chat_log.txt",
        mime="text/plain"
    )



# Session state to keep memory between turns
if "messages" not in st.session_state or st.session_state.get("active_role") != role:
    st.session_state.messages = [
        {"role": "system", "content": role_map[role]}
    ]
    st.session_state.active_role = role

# Display the chat so far
for msg in st.session_state.messages[1:]:  # skip system prompt
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_area("You:", height=80)
    submitted = st.form_submit_button("Send")

# 🟡 Important: this part stays outside the form block
if submitted:
    if uploaded_text:
        user_input += f"\n\nHere is the uploaded file content:\n{uploaded_text[:4000]}"

    print("==== USER INPUT SENT TO GPT ====")
    print(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content.strip()

    with open("chat_log_web.txt", "a") as log:
        log.write(f"You: {user_input}\nGPT: {reply}\n\n")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
