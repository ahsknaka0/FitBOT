import streamlit as st
from openai import OpenAI
import requests

st.title(":muscle: FitBOT")
st.divider()

# OpenAI API key
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Nutritionix API credentials
nutritionix_app_id = st.secrets["NUTRITIONIX_APP_ID"]
nutritionix_api_key = st.secrets["NUTRITIONIX_API_KEY"]

# set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What's Up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if the user is asking for dietary advice
    if "diet" in prompt.lower():
        # Call Nutritionix API for dietary information
        nutritionix_url = "https://api.nutritionix.com/v1_1/search/"
        params = {
            "appId": nutritionix_app_id,
            "appKey": nutritionix_api_key,
            "query": "healthy food",  # You can customize the query based on the user's input
        }
        nutritionix_response = requests.get(nutritionix_url, params=params)
        nutritionix_data = nutritionix_response.json()
        if "hits" in nutritionix_data and nutritionix_data["hits"]:
            food_item = nutritionix_data["hits"][0]["fields"]["item_name"]
            nutrition_info = nutritionix_data["hits"][0]["fields"]["nf_calories"]
            assistant_response = f"I recommend adding {food_item} to your diet. It contains approximately {nutrition_info} calories."
        else:
            assistant_response = "I couldn't find suitable dietary information at the moment."
    else:
        # Use OpenAI GPT-3.5-turbo for general fitness tips
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        assistant_response = st.write_stream(stream)

    # Display assistant message in chat message container
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": str(assistant_response)})
