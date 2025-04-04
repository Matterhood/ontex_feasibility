import streamlit as st
import requests
import json
from typing import List
import base64
from io import BytesIO
from PIL import Image
import os

# Configure the page
st.set_page_config(
    page_title="Packaging Evaluation Tool",
    page_icon="📦",
    layout="wide"
)

# Constants
API_URL = os.getenv("API_URL", "http://localhost:8000")  # Use environment variable with local fallback

def display_messages(messages: List[dict]):
    """Display the conversation messages in a chat-like interface."""
    for msg in messages:
        with st.chat_message(msg["agent"]):
            st.write(msg["content"])

def display_state(state: dict):
    """Display the current state of the evaluation."""
    with st.expander("Current State", expanded=False):
        st.json(state)

def main():
    st.title("📦 Packaging Evaluation Tool")
    
    # Initialize session state
    if "evaluation_state" not in st.session_state:
        st.session_state.evaluation_state = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar for input
    with st.sidebar:
        st.header("Input")
        packaging_concept = st.text_area(
            "Packaging Concept Description",
            height=200,
            help="Describe the packaging concept in detail"
        )
        
        uploaded_files = st.file_uploader(
            "Upload Concept Images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        
        if st.button("Start Evaluation"):
            if not packaging_concept:
                st.error("Please provide a packaging concept description")
                return
            
            # Convert images to base64
            concept_images = []
            for file in uploaded_files:
                if file is not None:
                    image = Image.open(file)
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    concept_images.append(f"data:image/png;base64,{img_str}")
            
            # Make API request
            try:
                response = requests.post(
                    f"{API_URL}/evaluate",
                    json={
                        "packaging_concept": packaging_concept,
                        "concept_images": concept_images
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # Update session state
                st.session_state.evaluation_state = result["state"]
                st.session_state.messages = result["messages"]
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {str(e)}")
    
    # Main content area
    if st.session_state.evaluation_state:
        # Display messages
        display_messages(st.session_state.messages)
        
        # Display state (collapsed by default)
        display_state(st.session_state.evaluation_state)
        
        # If waiting for human feedback
        if st.session_state.evaluation_state.get("awaiting_human_input"):
            st.info("Human feedback required")
            with st.form("feedback_form"):
                feedback = st.text_area("Your Feedback")
                submitted = st.form_submit_button("Submit Feedback")
                if submitted:
                    try:
                        response = requests.post(
                            f"{API_URL}/submit_feedback",
                            json={"feedback": feedback}
                        )
                        response.raise_for_status()
                        st.success("Feedback submitted successfully")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error submitting feedback: {str(e)}")

if __name__ == "__main__":
    main() 