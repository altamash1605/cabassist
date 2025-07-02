import streamlit as st
import pandas as pd
from datetime import date, timedelta
import base64
from supabase import create_client, Client
import requests
from datetime import datetime

st.markdown(
    """
    <link rel="shortcut icon" href="favicon.png">
    """,
    unsafe_allow_html=True
)


# --- Supabase Setup ---
url = "https://tpzujvdwuhxdtulebftj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwenVqdmR3dWh4ZHR1bGViZnRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0NTkzNTYsImV4cCI6MjA2NzAzNTM1Nn0.rIEIGYT1eUw0cog0WPwCnOSHS1Uk0cz_FLdXeu7kVgk"
supabase: Client = create_client(url, key)

# --- Logging Function ---
def log_event(event_type: str):
    try:
        ip_address = requests.get("https://api64.ipify.org?format=json").json()["ip"]
        supabase.table("analytics").insert({
            "event": event_type,
            "ip_address": ip_address,
        }).execute()
    except Exception as e:
        print(f"Logging error: {e}")

log_event("visit")

# --- Page Setup ---
st.set_page_config(page_title="CabAssist", page_icon="🚗", layout="centered")

# --- Inject favicon manually ---
st.markdown(
    """
    <head>
        <link rel="icon" href="favicon.png" type="image/png">
    </head>
    """,
    unsafe_allow_html=True
)

# --- Background Setup ---
def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .glass-box {{
            background: rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 2rem;
            margin: 4rem auto;
            width: 90%;
            max-width: 700px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }}
        .stTextInput input,
        .stTextArea textarea,
        .stDateInput input,
        .stCheckbox div,
        .stButton button,
        .stRadio div,
        label,
        h1, h2, h3, h4,
        .css-17eq0hr,
        .css-1v0mbdj {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("background.png")

# --- UI and Form ---
# (Keep your UI code unchanged after this)
# 👇 (You can paste the rest of your code from the form onwards)

