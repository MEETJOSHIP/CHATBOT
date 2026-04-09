# Llama-3 Powered Chatbot with Session Persistence CHATBOT

<img width="1919" height="905" alt="Screenshot 2026-04-09 154638" src="https://github.com/user-attachments/assets/e2e0a39d-4dd8-48d6-9156-aa63cd0f1aec" />

A full-stack AI chatbot application built with Streamlit and Groq Cloud API, featuring a multi-user authentication system and persistent chat history. This project mimics the ChatGPT user experience, allowing users to create, rename, and delete multiple chat sessions that are saved locally.

Key Features:
High-Speed Inference: Utilizes the llama-3.1-8b-instant model via Groq for near-instantaneous responses.  
User Authentication: Secure Sign-Up/Login system with SHA-256 password hashing.
Session Management: UUID-based chat tracking allowing for multiple independent conversations per user.
Data Persistence: Automatic JSON-based storage for user profiles and message history.
Context Awareness: Maintains the last 10 messages in the prompt buffer for coherent multi-turn conversations.

Tech Stack:
Frontend/App Framework: Streamlit
LLM Provider: Groq (Llama 3.1)
Data Handling: JSON, UUID, Hashlib
