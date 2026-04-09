import os
import json
import uuid
import hashlib
import streamlit as st
from groq import Groq

# ================== CONFIG ==================
st.set_page_config(
    page_title="ChatGPT-style Chatbot",
    page_icon="🤖",
    layout="wide"
)

USERS_FILE = "users.json"

# ================== HELPERS ==================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================== LOAD API KEY ==================
with open("config.json") as f:
    GROQ_API_KEY = json.load(f)["GROQ_API_KEY"]

client = Groq(api_key=GROQ_API_KEY)

# ================== SESSION STATE ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

users = load_users()

# ================== AUTH UI ==================
st.sidebar.title("🔐 Account")

if not st.session_state.logged_in:
    mode = st.sidebar.radio("Choose", ["Login", "Sign Up"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if mode == "Sign Up":
        if st.sidebar.button("Create Account"):
            if not username or not password:
                st.sidebar.warning("Fill all fields")
            elif username in users:
                st.sidebar.error("User already exists")
            else:
                users[username] = {
                    "password": hash_password(password),
                    "chats": {}
                }
                save_users(users)
                st.sidebar.success("Account created! Login now.")

    else:  # Login
        if st.sidebar.button("Login"):
            if (
                username in users and
                users[username]["password"] == hash_password(password)
            ):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.chats = users[username]["chats"]

                if not st.session_state.chats:
                    cid = str(uuid.uuid4())
                    st.session_state.chats[cid] = {
                        "title": "New Chat",
                        "messages": []
                    }
                    st.session_state.current_chat_id = cid
                else:
                    st.session_state.current_chat_id = next(iter(st.session_state.chats))

                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")

    st.stop()

# ================== LOGOUT ==================
st.sidebar.success(f"👋 {st.session_state.username}")

if st.sidebar.button("Logout"):
    users[st.session_state.username]["chats"] = st.session_state.chats
    save_users(users)
    st.session_state.clear()
    st.rerun()

# ================== SIDEBAR CHATS ==================
st.sidebar.divider()
st.sidebar.title("💬 Your Chats")

if st.sidebar.button("➕ New Chat"):
    cid = str(uuid.uuid4())
    st.session_state.chats[cid] = {
        "title": "New Chat",
        "messages": []
    }
    st.session_state.current_chat_id = cid
    users[st.session_state.username]["chats"] = st.session_state.chats
    save_users(users)
    st.rerun()

for cid, chat in list(st.session_state.chats.items()):
    col1, col2 = st.sidebar.columns([0.85, 0.15])

    if col1.button(chat["title"], key=f"open_{cid}"):
        st.session_state.current_chat_id = cid
        st.rerun()

    if col2.button("🗑️", key=f"del_{cid}"):
        del st.session_state.chats[cid]

        if st.session_state.current_chat_id == cid:
            if st.session_state.chats:
                st.session_state.current_chat_id = next(iter(st.session_state.chats))
            else:
                new_id = str(uuid.uuid4())
                st.session_state.chats[new_id] = {
                    "title": "New Chat",
                    "messages": []
                }
                st.session_state.current_chat_id = new_id

        users[st.session_state.username]["chats"] = st.session_state.chats
        save_users(users)
        st.rerun()

# ================== MAIN CHAT ==================
current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]

st.title("🤖 AI CHATBOT")

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Ask here...")

if user_prompt:
    messages.append({"role": "user", "content": user_prompt})

    if current_chat["title"] == "New Chat":
        current_chat["title"] = user_prompt[:30]

    with st.chat_message("user"):
        st.markdown(user_prompt)

    llm_messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        *messages[-10:]
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=llm_messages
    )

    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})

    users[st.session_state.username]["chats"] = st.session_state.chats
    save_users(users)

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
