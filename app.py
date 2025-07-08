import streamlit as st
import time
import uuid

# --- PAGE SETUP ---
st.set_page_config(
    page_title="ChatGPT Clone",
    page_icon="🤖",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* General body styling */
    body {
        background-color: #1E1E1E; /* A darker background */
        color: #E0E0E0;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #252526;
    }
    .css-1d391kg .stButton>button {
        border: 1px solid #4A4A4A;
        border-radius: 8px;
        background-color: transparent;
        color: #E0E0E0;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    .css-1d391kg .stButton>button:hover {
        background-color: #3A3A3A;
        color: #FFFFFF;
    }
    .css-1d391kg .stButton>button:focus {
        box-shadow: none;
    }

    /* Main chat area */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #2D2D2D;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #4A4A4A;
    }

    /* Chat input */
    .stChatInputContainer {
        background-color: #252526;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---

# Initialize chat sessions in session_state if not present
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

# Initialize current_chat_id if not present, or if it points to a deleted chat
if 'current_chat_id' not in st.session_state or st.session_state.current_chat_id not in st.session_state.chat_sessions:
    # If there are any existing chats, set the current chat to the first one
    if st.session_state.chat_sessions:
        st.session_state.current_chat_id = next(iter(st.session_state.chat_sessions))
    # Otherwise, create a new chat
    else:
        chat_id = str(uuid.uuid4())
        st.session_state.chat_sessions[chat_id] = {'title': 'New Chat', 'messages': []}
        st.session_state.current_chat_id = chat_id

# --- HELPER FUNCTIONS ---

def get_current_chat_messages():
    """Returns the messages of the currently active chat."""
    return st.session_state.chat_sessions[st.session_state.current_chat_id]['messages']

def get_current_chat_title():
    """Returns the title of the currently active chat."""
    return st.session_state.chat_sessions[st.session_state.current_chat_id]['title']

def set_current_chat_title(title):
    """Sets the title of the currently active chat."""
    st.session_state.chat_sessions[st.session_state.current_chat_id]['title'] = title

def stream_mock_response(prompt):
    """A mock generator function to simulate a streaming response."""
    response = f"Echo: {prompt}"
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# --- SIDEBAR ---
with st.sidebar:
    st.title("ChatGPT Clone")
    
    if st.button("➕ New Chat", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.chat_sessions[chat_id] = {'title': 'New Chat', 'messages': []}
        st.session_state.current_chat_id = chat_id
        st.rerun()

    st.markdown("---")
    st.markdown("### Chat History")

    # Display chat history with a delete button for each
    chat_ids = list(st.session_state.chat_sessions.keys())
    for chat_id in reversed(chat_ids):
        chat = st.session_state.chat_sessions[chat_id]
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(chat['title'], key=f"chat_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", use_container_width=True):
                if len(st.session_state.chat_sessions) > 1:
                    del st.session_state.chat_sessions[chat_id]
                    # If the deleted chat was the current one, switch to another
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = next(iter(st.session_state.chat_sessions))
                    st.rerun()
                else:
                    st.warning("Cannot delete the last chat.")

# --- MAIN CHAT INTERFACE ---

st.header(get_current_chat_title())

# Display chat messages
messages = get_current_chat_messages()
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Send a message..."):
    # Add user message to chat history
    messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if this is the first message in a "New Chat" to update the title later
    is_new_chat = get_current_chat_title() == "New Chat"

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Use the mock streaming function
        response_content = st.write_stream(stream_mock_response(prompt))

    # Add assistant response to chat history
    messages.append({"role": "assistant", "content": response_content})

    # If this is the first message in a "New Chat", update the title
    if is_new_chat:
        new_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
        set_current_chat_title(new_title)
        st.rerun() # Rerun to update the title in the sidebar