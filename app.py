import os
import json
import requests
import random
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
from datetime import datetime

# Configuration
import streamlit as st

# Load from secrets.toml
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL = st.secrets["RECIPIENT_EMAIL"]
BANGALORE_LOCATIONS = [
    "Koramangala", "Whitefield", "Indiranagar", "Jayanagar", "HSR Layout",
    "Electronic City", "Sarjapur Road", "Hebbal", "Yelahanka", "Bellandur"
]

IMAGE_SAVE_PATH = "generated_images"
os.makedirs(IMAGE_SAVE_PATH, exist_ok=True)

def generate_posts():
    location = random.choice(BANGALORE_LOCATIONS)
    prompt = (
        f"Generate 10 unique, engaging Facebook-style posts for a real estate professional in Bangalore.\n"
        f"Each post should:\n"
        f"- Begin with a strong hook or question to grab attention\n"
        f"- Include relevant emojis to make the post visually appealing\n"
        f"- Mention a specific Bangalore location (example: {location})\n"
        f'- Each post must include a title like one of these: "2BHK Flat in Whitefield", "Plot in Sarjapur Road", '
        f'"Villa in Kanakapura Road", "1BHK Flat in Koramangala", "2BHK Flat in Electronic City", '
        f'"3BHK Villa in Yelahanka", "Plot in Bannerghatta Road", "Individual House in Indiranagar"\n'
        f"- End with a natural-sounding call-to-action like 'DM us for more info' or 'Book a visit today'\n"
        f"- Optionally include a short market insight or statistic\n"
        f"- Add 3–5 trending hashtags related to real estate\n"
        f"- Optionally include a short buyer story (like 'Ravi just bought his first home')\n"
        f"- Include this in bold End with this line: ' Call us at +91 81219 75390 for more details.'\n\n"
        f"Return only a JSON array of posts (strings)."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500,
        "temperature": 0.8
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except:
            return [p.strip() for p in content.split('\n') if p.strip()]
    else:
        st.error(f"OpenRouter Error: {response.status_code} {response.text}")
        return []

def get_pexels_image(query):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("photos"):
            photo = data["photos"][0]
            return photo["src"]["large"], photo["photographer"]
    return None, None

# === Streamlit App ===
st.set_page_config(page_title="🏡 Real Estate Post Generator", layout="wide")
st.title("🏘️ Bangalore Real Estate Post Generator")
st.write("Generate 10 engaging posts + images for your real estate campaign.")

if st.button("Generate Posts"):
    posts = generate_posts()
    if not posts:
        st.error("Post generation failed.")
    else:
        st.success("✅ Posts generated!")
        for i, post in enumerate(posts):
            img_url, photographer = get_pexels_image("real estate bangalore")
            st.markdown(f"### Post #{i+1}")
            st.write(post)
            if img_url:
                st.image(img_url, caption=f"Photo by {photographer} on Pexels", use_column_width=True)
