import streamlit as st
import pandas as pd
from datetime import date, timedelta
import base64

# --- Page Setup ---
st.set_page_config(page_title="CabAssist", page_icon="🚗", layout="centered")

# --- Background Image Setup ---
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

# --- Form UI ---
with st.container():
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>CabAssist</h2>", unsafe_allow_html=True)

    with st.form("cab_form"):
        st.markdown("### 👤 Employee Input")
        emp_ids = st.text_area("Enter Employee IDs (one per line)", height=150)

        st.markdown("### 🗓️ Schedule Settings")
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

        next_day_logout = st.checkbox("🔁 Logout happens on next day", value=False)

        submit = st.form_submit_button("✅ Generate CSV")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Data Processing ---
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        date_range = pd.date_range(start=start_date, end=end_date)

        rows = []
        for emp_id in ids:
            if next_day_logout:
                for i, d in enumerate(date_range):
                    shift_date = d.strftime("%-d/%-m/%Y")
                    if i == 0:
                        # First day login only
                        rows.append({
                            "EmployeeId": emp_id,
                            "LogIn": shift_start,
                            "LogOut": "",
                            "LogInVenue": "",
                            "LogOutVenue": "",
                            "ShiftDate": shift_date,
                            "EditType": "ADD"
                        })
                    else:
                        rows.append({
                            "EmployeeId": emp_id,
                            "LogIn": shift_start,
                            "LogOut": shift_end,
                            "LogInVenue": "",
                            "LogOutVenue": "",
                            "ShiftDate": shift_date,
                            "EditType": "ADD"
                        })
                # Add logout-only row on the next day
                logout_day = end_date + timedelta(days=1)
                rows.append({
                    "EmployeeId": emp_id,
                    "LogIn": "",
                    "LogOut": shift_end,
                    "LogInVenue": "",
                    "LogOutVenue": "",
                    "ShiftDate": logout_day.strftime("%-d/%-m/%Y"),
                    "EditType": "ADD"
                })
            else:
                for d in date_range:
                    shift_date = d.strftime("%-d/%-m/%Y")
                    rows.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": shift_date,
                        "EditType": "ADD"
                    })

        df = pd.DataFrame(rows)
        st.success("✅ CSV Ready!")
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="moveinsync_schedule.csv", mime="text/csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- How to Use ---
st.markdown("""
    <div class="glass-box">
        <h4>📘 How to Use This Tool</h4>
        <ol>
            <li>Paste each Employee ID on a new line</li>
            <li>Select Start Date and End Date for scheduling</li>
            <li>Enter Shift Start and End times in 24-hour format (e.g., 22:30)</li>
            <li>✅ If your logout happens the next day, check <strong>‘Logout happens on next day’</strong></li>
            <li>Click <strong>Generate CSV</strong> to download the file</li>
            <li>Upload it to your <strong>MoveInSync</strong> admin panel</li>
        </ol>
        <p style="margin-top: 1rem;">ℹ️ Only one entry per date is generated — logout logic adjusts based on your checkbox selection.</p>
    </div>
""", unsafe_allow_html=True)
