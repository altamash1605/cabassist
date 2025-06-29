import streamlit as st
import pandas as pd
from datetime import date
import base64

# Page config
st.set_page_config(page_title="MoveInSync Cab Scheduler", page_icon="🚗", layout="centered")

# Function to set background from local image
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
        .main > div {{
            background-color: rgba(0, 0, 0, 0.65);
            padding: 2rem;
            border-radius: 12px;
            max-width: 700px;
            margin: auto;
        }}
        label, h1, .stTextInput, .stDateInput, .stTextArea, .stButton {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Apply background
set_background("background.png")

# Title
st.markdown("<h1 style='text-align: center; color: white;'>CabAssist</h1>", unsafe_allow_html=True)

# Form
with st.form("cab_form"):
    emp_ids = st.text_area("Employee IDs (one per line)")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", date.today())
    with col2:
        end_date = st.date_input("End Date", date.today())

    col3, col4 = st.columns(2)
    with col3:
        shift_start = st.text_input("Shift Start (HH:MM, 24hr)", "22:30")
    with col4:
        shift_end = st.text_input("Shift End (HH:MM, 24hr)", "08:00")

    submit = st.form_submit_button("Generate CSV")

# CSV generation
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        date_range = pd.date_range(start=start_date, end=end_date)

        rows = []
        for emp_id in ids:
            for d in date_range:
                rows.append({
                    "EmployeeId": emp_id,
                    "LogIn": shift_start,
                    "LogOut": shift_end,
                    "LogInVenue": "",
                    "LogOutVenue": "",
                    "ShiftDate": f"{d.day}/{d.month}/{d.year}",
                    "EditType": "ADD"
                })

        df = pd.DataFrame(rows)
        st.success("✅ CSV Ready!")
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="moveinsync_schedule.csv", mime="text/csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- How to Use: Info Glass Card ---
st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 2rem;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    ">
    <h4>🧾 How to Use</h4>
    <ol>
        <li>Paste each Employee ID on a new line</li>
        <li>Select the start and end date for scheduling</li>
        <li>Enter shift login and logout time in 24-hour format</li>
        <li>Click "Generate CSV" to download the formatted file</li>
        <li>Upload the CSV into MoveInSync dashboard</li>
    </ol>
    <p style="margin-top: 1rem;">ℹ️ The CSV is formatted automatically as per MoveInSync requirements.</p>
    </div>
""", unsafe_allow_html=True)

