import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
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

        skip_days = st.multiselect("Select Days to Skip (weekends, holidays)", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=["Saturday", "Sunday"])
        next_day_logout = st.checkbox("🔀 Logout happens on next day", value=False)

        submit = st.form_submit_button("✅ Generate CSV")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Data Processing ---
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        weekday_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        skip_indices = {weekday_map[d] for d in skip_days}

        full_dates = pd.date_range(start=start_date, end=end_date + timedelta(days=1))
        working_days = [d for d in full_dates if d.weekday() not in skip_indices and d <= end_date]

        rows = []
        for emp_id in ids:
            for i, day in enumerate(working_days):
                day_str = day.strftime("%-d/%-m/%Y")
                rows.append({"EmployeeId": emp_id, "LogIn": shift_start, "LogOut": "", "LogInVenue": "", "LogOutVenue": "", "ShiftDate": day_str, "EditType": "ADD"})

                next_day = day + timedelta(days=1)
                if next_day > end_date + timedelta(days=1):
                    continue

                if (i == len(working_days) - 1) or (working_days[i + 1] != next_day):
                    next_day_str = next_day.strftime("%-d/%-m/%Y")
                    rows.append({"EmployeeId": emp_id, "LogIn": "", "LogOut": shift_end, "LogInVenue": "", "LogOutVenue": "", "ShiftDate": next_day_str, "EditType": "ADD"})

        df = pd.DataFrame(rows)
        st.success("✅ CSV Ready!")
        st.download_button("📅 Download CSV", df.to_csv(index=False), file_name="moveinsync_schedule.csv", mime="text/csv")

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
            <li>Select which days to skip (like weekends)</li>
            <li>✅ If your logout happens the next day, check <strong>‘Logout happens on next day’</strong></li>
            <li>Click <strong>Generate CSV</strong> to download the file</li>
            <li>Upload it to your <strong>MoveInSync</strong> admin panel</li>
        </ol>
        <p style="margin-top: 1rem;">Only one entry per date is generated — logout logic adjusts based on your checkbox selection.</p>
    </div>
""", unsafe_allow_html=True)
