import streamlit as st
from streamlit_chat import message
import json
import os
from datetime import datetime
import ollama
from time import sleep
from pathlib import Path

# === Paths ===
DATA_DIR = "noorbot_data"
os.makedirs(DATA_DIR, exist_ok=True)

FILES = {
    "duas": os.path.join(DATA_DIR, "duas.json"),
    "affirmations": os.path.join(DATA_DIR, "affirmations.json"),
    "gratitude": os.path.join(DATA_DIR, "gratitude.json"),
    "journals": os.path.join(DATA_DIR, "journals.json"),
    "chat_log": os.path.join(DATA_DIR, "chat_log.json"),
    "chat_conversations": os.path.join(DATA_DIR, "chat_conversations.json")  # New file for conversation list
}

# === Helpers ===
def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_timestamp(ts):
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%d %b, %I:%M %p")

def toggle_favorite(section, index):
    data = load_data(FILES[section])
    data[index]['favorite'] = not data[index].get('favorite', False)
    save_data(FILES[section], data)

def delete_entry(section, index):
    data = load_data(FILES[section])
    data.pop(index)
    save_data(FILES[section], data)

def update_entry(section, index, title, content):
    data = load_data(FILES[section])
    data[index]['title'] = title
    data[index]['content'] = content
    data[index]['timestamp'] = datetime.now().isoformat()
    save_data(FILES[section], data)

def save_entry(section, title, content):
    data = load_data(FILES[section])
    data.append({
        "title": title,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "favorite": False
    })
    save_data(FILES[section], data)

def render_card(entry, section, index):
    ts = format_timestamp(entry["timestamp"])
    favorite = entry.get("favorite", False)
    
    if st.session_state.get(f'edit_{section}') == index:
        with st.form(key=f'edit_form_{section}_{index}'):
            edit_title = st.text_input("Title", value=entry['title'], key=f"edit_title_input_{section}_{index}")
            edit_content = st.text_area("Content", value=entry['content'], key=f"edit_content_input_{section}_{index}")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save"):
                    update_entry(section, index, edit_title, edit_content)
                    st.session_state[f'edit_{section}'] = None
                    st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state[f'edit_{section}'] = None
                    st.rerun()
    else:
        # Create a container for the card
        card = st.container(border=True)
        with card:
            # Create columns for the title and buttons
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"<h4 style='margin-top:0;'>{entry['title']}</h4>", unsafe_allow_html=True)
            
            with col2:
                # Create columns for the three buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if st.button("❤" if favorite else "♡", key=f"fav_{section}_{index}"):
                        toggle_favorite(section, index)
                        st.rerun()
                
                with btn_col2:
                    if st.button("✎", key=f"edit_{section}_{index}"):
                        st.session_state[f'edit_{section}'] = index
                        st.session_state[f'edit_title_{section}'] = entry['title']
                        st.session_state[f'edit_content_{section}'] = entry['content']
                        st.rerun()
                
                with btn_col3:
                    if st.button("🗑", key=f"del_{section}_{index}"):
                        delete_entry(section, index)
                        st.rerun()
            
            # Display the content
            st.markdown(f"<p style='white-space: pre-wrap;'>{entry['content']}</p>", unsafe_allow_html=True)
            
            # Display the timestamp
            st.markdown(f"<div style='text-align: right; font-size: 0.8em; color: #7f8c8d;'>{ts}</div>", unsafe_allow_html=True)
            
            # Add some styling to the container
            st.markdown(
                f"""
                <style>
                    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="element-container"] > div.stMarkdown > h4) {{
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 15px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        border: 15px solid #008080;
                    }}
                </style>
                """,
                unsafe_allow_html=True
            )

def render_section(section):
    data = load_data(FILES[section])
    
    # Sort with favorites first, then newest first
    data.sort(key=lambda x: (
        not x.get('favorite', False),  # Favorites first
        -datetime.fromisoformat(x['timestamp']).timestamp()  # Newest first
    ))
    
    if st.button(f"✚ New {section.capitalize()}", key=f"new_{section}"):
        st.session_state[f'show_form_{section}'] = not st.session_state.get(f'show_form_{section}', False)
    
    if st.session_state.get(f'show_form_{section}', False):
        with st.form(key=f'form_{section}'):
            title = st.text_input("Title", key=f"title_{section}")
            content = st.text_area("Content", key=f"content_{section}")
            if st.form_submit_button("Save"):
                if content:
                    save_entry(section, title, content)
                    st.session_state[f'show_form_{section}'] = False
                    st.rerun()
            if st.form_submit_button("Cancel"):
                st.session_state[f'show_form_{section}'] = False
    
    # Create a copy of the original data before sorting to maintain correct indices
    original_data = load_data(FILES[section])
    
    # Display all entries in the sorted order but use original indices for operations
    for display_idx, entry in enumerate(data):
        # Find the original index of this entry
        original_index = next((i for i, item in enumerate(original_data) 
                            if item['timestamp'] == entry['timestamp'] and 
                            item['title'] == entry['title'] and 
                            item['content'] == entry['content']), None)
        
        if original_index is not None:
            render_card(entry, section, original_index)

def load_conversations():
    if not os.path.exists(FILES["chat_conversations"]):
        return []
    return load_data(FILES["chat_conversations"])

def save_conversations(conversations):
    save_data(FILES["chat_conversations"], conversations)

def get_current_conversation_id():
    if 'current_conversation_id' not in st.session_state:
        return 0
    return st.session_state.current_conversation_id

def ensure_conversation_exists():
    if 'current_conversation_id' not in st.session_state:
        return False
    return True

def get_conversation_messages(conversation_id):
    chat_data = load_data(FILES["chat_log"])
    return [msg for msg in chat_data if msg.get("conversation_id") == conversation_id]

# === Chatbot ===
def handle_chat(user_input):
    conversation_id = get_current_conversation_id()
    
    # Get previous messages in this conversation
    previous_messages = get_conversation_messages(conversation_id)
    
    # Prepare the message history for the model
    messages_for_model = []
    
    # System prompt
    system_prompt = """
    You are a wise, kind, and emotionally supportive Islamic scholar and spiritual guide.
    Your role is to respond with deep empathy, gentle wisdom, and a sound understanding of Islamic teachings. Your primary goal is to help the user feel seen, heard, spiritually supported, and gently guided toward healing and growth.
    
    When a user shares a personal struggle or question:
    - Reflect on their situation using relevant Islamic principles.
    - Share short, relevant duas.
    - Include uplifting affirmations rooted in hope, patience, and Allah’s mercy.
    - Never blame or shame. Always guide with kindness, humility, and compassion.
    - Use respectful, soft, and encouraging language — warm and non-judgmental.
    - Do not assume the user is a scholar. Explain Islamic teachings simply and clearly.
    - Avoid issuing strict rulings unless explicitly asked. Prioritize emotional support and spiritual encouragement.
    - When relevant, offer practical, gentle advice for personal or emotional healing.
    - Keep it shorter, to not overwhelm the user emotionally.

    Tone: Soothing, heart-centered, non-authoritative, and deeply compassionate — always nurturing the user’s relationship with Allah.

    Always remember: Your purpose is not only to inform, but to *heal*, *comfort*, and *inspire sincere connection with Allah (SWT)*.
    """
    
    messages_for_model.append({"role": "system", "content": system_prompt})
    
    # Add previous conversation history - up to 4 messages (2 exchanges)
    for msg in previous_messages[-4:]:
        messages_for_model.append({"role": "user", "content": msg["user"]})
        messages_for_model.append({"role": "assistant", "content": msg["bot"]})
    
    # Add the new user message
    messages_for_model.append({"role": "user", "content": user_input})
    
    # Start chat with context
    response = ollama.chat(
        model="gemma3:1b",
        messages=messages_for_model,
        stream=True
    )
    
    response_placeholder = st.empty()
    full_response = ""
    
    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            full_response += chunk['message']['content']
            response_placeholder.markdown(f"""
            <div style='
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                {full_response}
            </div>
            """, unsafe_allow_html=True)
            sleep(0.05)
    
    # Save to chat log
    chat_data = load_data(FILES["chat_log"])
    chat_data.append({
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "user": user_input,
        "bot": full_response
    })
    save_data(FILES["chat_log"], chat_data)
    
    # Update conversation title if it's the first message
    if len(previous_messages) == 0:  # This is the first message
        conversations = load_conversations()
        for conv in conversations:
            if conv["id"] == conversation_id:
                conv["title"] = " ".join(user_input.split()[:5]) + "..."
                break
        save_conversations(conversations)
    
    return full_response

# === UI Setup ===
st.set_page_config(
    page_title="NoorBot",
    page_icon="🕊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        border-radius: 8px;
        padding: 0.25rem 0.5rem;
        margin: 0;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stMarkdown {
        line-height: 1.6;
    }
    
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <h1 style='
            font-size: 48px;
            font-weight: 700;
        '>
            <span style='color:#008080;'>🕊</span>
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("Your Islamic guide and companion")
    st.markdown("---")
    page = st.radio("Open your heart to...", ["Chat", "Duas", "Affirmations", "Gratitude", "Journals"])

# Main Content
if page == "Chat":
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@700&display=swap" rel="stylesheet">
        <h1 style='
            font-family: "Tajawal", sans-serif;
            font-size: 48px;
            font-weight: 700;
        '>
            <span style='color:#008080;'>Noor</span><span style='color:#B87333;'>Bot</span>
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("اللهم إني أسألك العفو والعافية في الدنيا والآخرة")
    st.markdown("Share your feelings or problems for Islamic guidance and wisdom.")
    
    # Conversation management
    with st.sidebar:
        st.markdown("### Chats")
        
        # New Chat button
        if st.button("✚ New Chat"):
            conversations = load_conversations()
            new_id = datetime.now().isoformat()
            conversations.append({
                "id": new_id,
                "title": f"Conversation {len(conversations) + 1}",
                "timestamp": new_id
            })
            save_conversations(conversations)
            st.session_state.current_conversation_id = new_id
            st.session_state.chat_history = []
            st.rerun()
        
        # List of conversations
        conversations = load_conversations()
        conversations.sort(key=lambda x: x["timestamp"], reverse=True)
        current_conv_id = get_current_conversation_id()

        for conv in conversations:
            col1, col2 = st.columns([4, 1])
            with col1:
                active_class = "active-chat" if conv["id"] == current_conv_id else ""
                if st.button(
                    f"{conv['title']}",
                    key=f"conv_{conv['id']}",
                    use_container_width=True
                ):
                    if conv["id"] != current_conv_id:
                        st.session_state.current_conversation_id = conv["id"]
                        st.rerun()
                    if conv["id"] == current_conv_id:
                        st.markdown(
                            f"""
                            <script>
                                document.addEventListener('DOMContentLoaded', function() {{
                                    const buttons = parent.document.querySelectorAll('button[data-testid="baseButton-secondary"]');
                                    buttons.forEach(button => {{
                                        if (button.textContent.trim() === "{conv['title']}") {{
                                            button.classList.add('{active_class}');
                                        }}
                                    }});
                                }});
                            </script>
                            """,
                            unsafe_allow_html=True
                        )

            with col2:
                if st.button("🗑", key=f"del_{conv['id']}"):
                    # Delete conversation messages
                    chat_data = load_data(FILES["chat_log"])
                    chat_data = [msg for msg in chat_data if msg.get("conversation_id") != conv["id"]]
                    save_data(FILES["chat_log"], chat_data)
                    
                    # Delete conversation entry
                    conversations = [c for c in conversations if c["id"] != conv["id"]]
                    save_conversations(conversations)
                    
                    # If we're deleting the current conversation, start a new one
                    if st.session_state.get("current_conversation_id") == conv["id"]:
                        st.session_state.pop("current_conversation_id")
                    st.rerun()
    
    # Get current conversation messages
    conversation_id = get_current_conversation_id()
    conversation_messages = get_conversation_messages(conversation_id)
    
    # Display chat history
    for msg in conversation_messages:
        user_msg = msg["user"]
        bot_msg = msg["bot"]
        
        user_width = min(20 + len(user_msg) * 0.5, 90)
        st.markdown(f"""
        <div style='
            margin-top: 0px;
            border-radius: 4px;
            padding: 10px 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: {user_width}%;
            margin-left: auto;
            word-wrap: break-word;
        '>
            {user_msg}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='
            margin-top: 0px;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        '>
            {bot_msg}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your feeling or problem...")
    
    if user_input:
        if not ensure_conversation_exists():
            conversations = load_conversations()
            new_id = datetime.now().isoformat()
            conversations.append({
                "id": new_id,
                "title": " ".join(user_input.split()[:5]) + "...",
                "timestamp": new_id
            })
            save_conversations(conversations)
            st.session_state.current_conversation_id = new_id

        user_width = min(20 + len(user_input) * 0.5, 90)
        # Display user message immediately
        st.markdown(f"""
        <div style='
            margin-top: 0px;
            border-radius: 4px;
            padding: 10px 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: {user_width}%;
            margin-left: auto;
            word-wrap: break-word;
        '>
            {user_input}
        </div>
        """, unsafe_allow_html=True)
        
        # Get and stream bot response
        bot_response = handle_chat(user_input)
        
        # Rerun to update the display
        st.rerun()
  
elif page == "Duas":
    st.title("Duas")
    render_section("duas")

elif page == "Affirmations":
    st.title("Affirmations")
    render_section("affirmations")

elif page == "Gratitude":
    st.title("Gratitude Journal")
    render_section("gratitude")

elif page == "Journals":
    st.title("Journals")
    render_section("journals")
