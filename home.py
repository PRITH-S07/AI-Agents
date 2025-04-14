import streamlit as st
import requests
from datetime import datetime, timedelta
from uuid import uuid4
import json
import fitz
import re

st.title("📘 CMU Course Recommender")
st.write("AI-powered course suggestions based on your interests and preferences!")

# Sidebar for filters
with st.sidebar:
    st.header("🎯 Preferences")
    hours_per_week = st.slider("Hours per week", 1, 20, (5, 10))
    course_rating = st.slider("Course rating", 1.0, 5.0, (3.5, 5.0), step=0.1)

# Collect user input
auto_interests = ""
st.subheader("💬 Tell us about yourself")
interests = st.text_area("What topics are you interested in?", value=auto_interests)

past_courses = st.multiselect(
    "Courses you've already taken:",
    options=["15-319: Cloud Computing", "15-351: Algorithms", "15-213: Computer Systems"]
)

resume = st.file_uploader("📄 Upload your resume (PDF only)", type=['pdf'])



if resume:
    try:
        doc = fitz.open(stream=resume.read(), filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        # Naive interest extractor (expand with NLP later)
        matches = re.findall(r"(cloud computing|machine learning|systems|AI|networking|security|NLP|databases|robotics|computer vision)", full_text, re.IGNORECASE)
        unique_matches = set(match.lower() for match in matches)
        if unique_matches:
            auto_interests = ", ".join(sorted(unique_matches))
            st.success(f"📌 Interests detected from resume: {auto_interests}")
    except Exception as e:
        st.error(f"Failed to parse resume: {str(e)}")

# ICS Calendar helper
def create_ics(title, course_id, day, start, end, location, reason):
    days = {"Monday": "MO", "Tuesday": "TU", "Wednesday": "WE", "Thursday": "TH", "Friday": "FR"}
    if day not in days:
        return "Invalid day"
    today = datetime.today()
    diff = (list(days.keys()).index(day) - today.weekday() + 7) % 7
    event_date = today + timedelta(days=diff)
    start_dt = datetime.strptime(f"{event_date.date()} {start}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{event_date.date()} {end}", "%Y-%m-%d %H:%M")
    uid = uuid4()
    return f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//CMU Advisor//EN\nBEGIN:VEVENT\nUID:{uid}@cmu.edu\nDTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\nDTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\nDTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\nSUMMARY:{title} ({course_id})\nLOCATION:{location}\nDESCRIPTION:{reason}\nRRULE:FREQ=WEEKLY;COUNT=15;BYDAY={days[day]}\nEND:VEVENT\nEND:VCALENDAR"""

# Query LlamaIndex API
def query_llm(interests, past_courses, hours, rating):
    query = f"""I'm interested in {interests}.
I’ve already taken: {', '.join(past_courses) if past_courses else 'no courses yet'}.
I prefer courses that take {hours[0]}–{hours[1]} hours/week and have ratings between {rating[0]}–{rating[1]}.
Based on CMU's course catalog, what do you recommend?"""
    try:
        res = requests.post("http://127.0.0.1:5000/query", json={"query": query})
        res.raise_for_status()
        return res.json().get("response", "Sorry, no response received.")
    except Exception as e:
        return f"Error: {str(e)}"

# Extract course metadata using regex (basic)
def extract_course_info_from_json(response_text):
    try:
        cleaned = response_text.strip().strip("`").strip("json")
        data = json.loads(cleaned)
        return data.get("courses", [])
    except json.JSONDecodeError:
        return []


# Button to trigger recommendation
if st.button("✨ Recommend Courses"):
    with st.spinner("Analyzing your profile and finding the best matches..."):
        response = query_llm(interests, past_courses, hours_per_week, course_rating)
        with st.chat_message("assistant"):
            st.markdown(response)

            # Extract course info (basic)
            courses = extract_course_info_from_json(response)
            if not courses:
                # Try fallback — extract quoted course name
                fallback_match = re.search(r'"([^"]+)"', response)
                if fallback_match:
                    course_title = fallback_match.group(1)
                    course_id = "Unknown-ID"
                    day = "Monday"
                    start = "10:00"
                    end = "11:20"
                    location = "TBD"
                    reason = "Suggested by advisor based on your resume and interests."

                    st.markdown(f"**{course_title}**")

                    ics_content = create_ics(
                        course_title, course_id, day, start, end, location, reason
                    )

                    st.download_button(
                        label=f"📅 Add to Calendar",
                        data=ics_content,
                        file_name=f"{course_title.replace(' ', '_')}.ics",
                        mime="text/calendar"
                    )
                else:
                    st.warning("⚠️ Couldn't extract any structured or fallback course info.")
