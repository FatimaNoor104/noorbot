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

### App interface
- **Chat**
    - All previous conversations are saved and displayed in the left sidebar for quick access.
    - Users can select any chat to view, continue, or delete.

    <img width="1919" height="976" alt="Screenshot 2025-07-27 010931" src="https://github.com/user-attachments/assets/0faf1e63-1eea-4b37-bee3-f9c619785b81" />

- **Dua, Affirmations, Journals, Gratitude Pages**
    - All sections have a consistent layout.
    - Users can:
        - Add new entries with optional titles.
        - Mark entries as favorite.
        - Edit or delete any entry.

    <img width="1918" height="968" alt="Screenshot 2025-07-27 010912" src="https://github.com/user-attachments/assets/a6aae872-f16a-420e-9f14-a06f44fea4f9" />


## Developer

- [Fatima Noor](https://www.linkedin.com/in/fatima-nur/)
