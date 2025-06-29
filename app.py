import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import base64

# --- Background Setup ---
def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    .glass-box {{
        background: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        width: 90%;
        max-width: 700px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }}
    .stTextInput input, .stTextArea textarea, .stDateInput input,
    .stCheckbox div, .stButton button, label, h1, h2, h3, h4 {{
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Setup ---
st.set_page_config(page_title="CabAssist", page_icon="🚗", layout="centered")
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

        next_day_logout = st.checkbox("🔁 Logout happens on next day", value=True)

        weekday_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        skip_days = st.multiselect("❌ Skip These Days", list(weekday_map.keys()), default=["Saturday", "Sunday"])
        skip_indices = set(weekday_map[d] for d in skip_days)

        submit = st.form_submit_button("✅ Generate CSV")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Logic Execution ---
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        all_dates = pd.date_range(start=start_date, end=end_date + timedelta(days=1))  # include next-day logout
        working_days = [d for d in all_dates if d.weekday() not in skip_indices and d <= end_date]

        data = []

        for emp_id in ids:
            last_login_date = None

            for i, current_day in enumerate(all_dates):
                date_str = current_day.strftime("%-d/%-m/%Y")
                prev_day = current_day - timedelta(days=1)
                is_working = current_day in working_days
                was_prev_working = prev_day in working_days

                if current_day == working_days[0]:
                    # First working day → Login only
                    data.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": "",
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": date_str,
                        "EditType": "ADD"
                    })
                    last_login_date = current_day

                elif current_day in working_days[:-1] and current_day != working_days[0]:
                    # Middle working days → Login + Logout
                    data.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": date_str,
                        "EditType": "ADD"
                    })
                    last_login_date = current_day

                elif current_day == working_days[-1]:
                    # Last working day → Login only
                    data.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": "",
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": date_str,
                        "EditType": "ADD"
                    })
                    last_login_date = current_day

                elif not is_working and was_prev_working:
                    # Skipped day but previous day had login → logout only
                    data.append({
                        "EmployeeId": emp_id,
                        "LogIn": "",
                        "LogOut": shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": date_str,
                        "EditType": "ADD"
                    })

                elif current_day == working_days[-1] + timedelta(days=1):
                    # Next day after last working → logout only
                    data.append({
                        "EmployeeId": emp_id,
                        "LogIn": "",
                        "LogOut": shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": date_str,
                        "EditType": "ADD"
                    })

        df = pd.DataFrame(data)
        st.success("✅ CSV Generated!")
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="moveinsync_schedule_v1.2.csv", mime="text/csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- Help Section ---
st.markdown("""
<div class="glass-box">
<h4>📘 How to Use CabAssist</h4>
<ol>
<li>Paste employee IDs (one per line)</li>
<li>Set shift timings and select start/end dates</li>
<li>Choose whether logout is on the next day</li>
<li>Select which days to skip (e.g., weekends)</li>
<li>Click 'Generate CSV' and upload to MoveInSync</li>
</ol>
<p style="margin-top: 1rem;">ℹ️ Output auto-handles skipped days and logout continuity</p>
</div>
""", unsafe_allow_html=True)
