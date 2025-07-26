# NoorBot — Offline Islamic AI Companion

**NoorBot** is a private, offline Islamic journaling and AI chatbot app built with Streamlit and Ollama. It offers local chat with a compassionate LLM (Gemma) and tools for journaling, gratitude, affirmations, and duas — all stored securely on your device.

---

## Features
- **Chatbot**: Local AI chat using Gemma via Ollama
- **Journals**: Add, edit, delete, and favorite personal journal entries
- **Duas & Affirmations**: Save and organize duas and affirmations
- **Gratitude Tracker**: Log and reflect on daily blessings
- **Fully Private**: All data stored locally in JSON (no accounts, no cloud)

---

## Technologies Used
- Python
- Streamlit (frontend and UI)
- Ollama (local LLM engine)
- Gemma 3:1b (LLM model)
- JSON-based local storage (no database or cloud dependency)

---
## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
2. **Install Ollama + Gemma**:
    ```bash
    ollama run gemma3:1b
3. **Run App**:
    ```bash
    streamlit run main.py
---

## Local Data Storage
All user data is saved in the noorbot_data/ folder as JSON files:
- chat_conversations.json
- duas.json
- affirmations.json
- gratitude.json
- journals.json

---

## Developer
Created by [Fatima Noor](https://www.linkedin.com/in/fatima-nur/)
