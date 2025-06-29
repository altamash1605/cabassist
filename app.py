import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import base64

# --- Page Setup ---
st.set_page_config(page_title="CabAssist", page_icon="🚗", layout="centered")

# --- Background Image ---
def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    st.markdown(f"""
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
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }}
        .stTextInput input, .stTextArea textarea, .stDateInput input,
        .stCheckbox div, .stButton button, label, h1, h2, h3, h4,
        .css-17eq0hr, .css-1v0mbdj {{
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("background.png")

# --- UI ---
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
        weekday_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2,
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        skip_days = st.multiselect("❌ Skip These Days", list(weekday_map.keys()), default=["Saturday", "Sunday"])
        skip_indices = set(weekday_map[d] for d in skip_days)

        submit = st.form_submit_button("✅ Generate CSV")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Generate CSV ---
if submit:
    try:
        ids = [e.strip() for e in emp_ids.strip().split("\n") if e.strip()]
        all_dates = pd.date_range(start=start_date, end=end_date)

        rows = []
        for emp_id in ids:
            for d in all_dates:
                if d.weekday() in skip_indices:
                    rows.append({
                        "EmployeeId": emp_id,
                        "LogIn": "",
                        "LogOut": "",
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": d.strftime("%-d/%-m/%Y"),
                        "EditType": "ADD"
                    })
                elif not next_day_logout:
                    rows.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": shift_end,
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": d.strftime("%-d/%-m/%Y"),
                        "EditType": "ADD"
                    })
                else:
                    # Login only on this day
                    rows.append({
                        "EmployeeId": emp_id,
                        "LogIn": shift_start,
                        "LogOut": "",
                        "LogInVenue": "",
                        "LogOutVenue": "",
                        "ShiftDate": d.strftime("%-d/%-m/%Y"),
                        "EditType": "ADD"
                    })

                    # Logout on next day if not skipped
                    logout_day = d + timedelta(days=1)
                    if logout_day <= end_date and logout_day.weekday() not in skip_indices:
                        rows.append({
                            "EmployeeId": emp_id,
                            "LogIn": "",
                            "LogOut": shift_end,
                            "LogInVenue": "",
                            "LogOutVenue": "",
                            "ShiftDate": logout_day.strftime("%-d/%-m/%Y"),
                            "EditType": "ADD"
                        })

        # Convert to DataFrame
        df = pd.DataFrame(rows)
        df["ShiftDate_dt"] = pd.to_datetime(df["ShiftDate"], format="%d/%m/%Y")

        # Merge rows with same date and employee
        merged_df = df.groupby(["EmployeeId", "ShiftDate_dt"], as_index=False).agg({
            "LogIn": "max",
            "LogOut": "max",
            "LogInVenue": "first",
            "LogOutVenue": "first",
            "EditType": "first"
        })
        merged_df["ShiftDate"] = merged_df["ShiftDate_dt"].dt.strftime("%-d/%-m/%Y")
        merged_df.drop(columns="ShiftDate_dt", inplace=True)

        # Handle last entry: login only
        merged_df = merged_df.sort_values("ShiftDate")
        for i in range(len(merged_df) - 1, -1, -1):
            row = merged_df.iloc[i]
            if row["LogIn"] and row["LogOut"]:
                login_row = row.copy()
                logout_row = row.copy()
                login_row["LogOut"] = ""
                logout_row["LogIn"] = ""
                logout_row["ShiftDate"] = (datetime.strptime(login_row["ShiftDate"], "%d/%m/%Y") + timedelta(days=1)).strftime("%-d/%-m/%Y")
                merged_df = pd.concat([merged_df.iloc[:i], pd.DataFrame([login_row, logout_row]), merged_df.iloc[i+1:]], ignore_index=True)
                break

        merged_df = merged_df.sort_values("ShiftDate")
        st.success("✅ CSV Ready!")
        st.download_button("📥 Download CSV", merged_df.to_csv(index=False), file_name="moveinsync_schedule.csv", mime="text/csv")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# --- How to Use ---
st.markdown("""
<div class="glass-box">
<h4>📘 How to Use This Tool</h4>
<ol>
    <li>Paste Employee IDs (one per line)</li>
    <li>Select shift date range</li>
    <li>Set shift timings (24hr format)</li>
    <li>Check “Logout happens on next day” if applicable</li>
    <li>Skip weekends or custom days</li>
    <li>Click Generate CSV and upload to MoveInSync</li>
</ol>
<p>ℹ️ Last shift ends the next morning; the logic ensures no duplicates and accurate logout days.</p>
</div>
""", unsafe_allow_html=True)
