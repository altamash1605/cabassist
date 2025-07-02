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

        skip_days = st.multiselect("Select Days to Skip", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=["Saturday", "Sunday"])
        next_day_logout = st.checkbox("🔁 Logout happens on next day", value=False)
        edit_type = st.radio("Edit Type", ["ADD", "DELETE"], horizontal=True)

        submit = st.form_submit_button("✅ Generate CSV")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Data Processing ---
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        weekday_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        skip_indices = {weekday_map[d] for d in skip_days}

        all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 2)]
        raw_rows = []

        for emp_id in ids:
            for i, current_date in enumerate(all_dates[:-1]):
                next_date = current_date + timedelta(days=1)
                weekday = current_date.weekday()

                if weekday not in skip_indices:
                    shift_date_str = current_date.strftime("%-d/%-m/%Y")
                    raw_rows.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": "" if next_day_logout else shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": shift_date_str,
                        "EditType": edit_type
                    })

                    if next_day_logout:
                        logout_shift_date = next_date.strftime("%-d/%-m/%Y")
                        raw_rows.append({
                            "EmployeeId": emp_id,
                            "LogIn": "",
                            "LogOut": shift_end,
                            "LogInVenue": "",
                            "LogOutVenue": "",
                            "ShiftDate": logout_shift_date,
                            "EditType": edit_type
                        })
                else:
                    if next_day_logout and i > 0:
                        prev_date = all_dates[i - 1]
                        if prev_date.weekday() not in skip_indices:
                            logout_shift_date = current_date.strftime("%-d/%-m/%Y")
                            raw_rows.append({
                                "EmployeeId": emp_id,
                                "LogIn": "",
                                "LogOut": shift_end,
                                "LogInVenue": "",
                                "LogOutVenue": "",
                                "ShiftDate": logout_shift_date,
                                "EditType": edit_type
                            })

        # Smart merge: one row per employee + date
        merged_rows = {}
        for row in raw_rows:
            key = (row['EmployeeId'], row['ShiftDate'])
            if key not in merged_rows:
                merged_rows[key] = row
            else:
                if not merged_rows[key]['LogIn'] and row['LogIn']:
                    merged_rows[key]['LogIn'] = row['LogIn']
                if not merged_rows[key]['LogOut'] and row['LogOut']:
                    merged_rows[key]['LogOut'] = row['LogOut']

        df = pd.DataFrame(merged_rows.values())
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
            <li>Select <strong>ADD</strong> or <strong>DELETE</strong> to reflect the Edit Type in your CSV</li>
            <li>Click <strong>Generate CSV</strong> to download the file</li>
            <li>Upload it to your <strong>MoveInSync</strong> admin panel</li>
        </ol>
        <p style="margin-top: 1rem;">Each date has only one row per employee. Logout-only entries on skipped days are preserved.</p>
    </div>
""", unsafe_allow_html=True)

