import streamlit as st
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Title
st.title("CMU Course Recommender")
st.write("Here to help you decide what courses to take by browsing through CMU syllabus, FCE hours etc")

# Sidebar for Preferences
with st.sidebar:
    st.header("Preferences")
    hours_per_week = st.slider("Hours per week", min_value=1, max_value=20, value=(5, 10))
    course_rating = st.slider("Course rating", min_value=1.0, max_value=5.0, value=(3.5, 5.0), step=0.1)

# Chat Interface
st.markdown("---")
st.subheader("Tell me more about yourself")


# Interests input
interests = st.text_area("What topics interest you? (e.g., machine learning, cloud computing, algorithms)")
past_courses = st.multiselect(
    "Courses you've already completed (optional)",
    options=["15-319: Cloud Computing", "15-351: Algorithms", "15-213: Intro to Computer Systems"]
)

# Resume upload
resume = st.file_uploader("📄 Upload your resume (optional)", type=['pdf', 'txt', 'docx'])

# Mock recommendation engine
def mock_recommendations(interests, resume, past_courses, hrs, rating):
    # This could later parse the resume and interests
    courses = [
        {"course_id": "15-319", "title": "Cloud Computing", "reason": "Great for cloud infrastructure roles.", "day": "Monday", "start": "15:30", "end": "17:00", "location": "GHC 7006", "rating": 4.5},
        {"course_id": "15-351", "title": "Algorithms and Advanced Data Structures", "reason": "Crucial for algorithmic thinking.", "day": "Wednesday", "start": "09:00", "end": "09:50", "location": "DH 2210", "rating": 4.7},
    ]
    # Just return all courses for now, could be smarter based on resume/interests
    return [c for c in courses if rating[0] <= c["rating"] <= rating[1]]

# Generate .ics event
def create_ics(course):
    days = {"Monday": "MO", "Tuesday": "TU", "Wednesday": "WE", "Thursday": "TH", "Friday": "FR"}
    today = datetime.today()
    diff = (list(days.keys()).index(course["day"]) - today.weekday() + 7) % 7
    event_date = today + timedelta(days=diff)
    start_dt = datetime.strptime(f"{event_date.date()} {course['start']}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{event_date.date()} {course['end']}", "%Y-%m-%d %H:%M")
    uid = uuid4()
    return f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//CMU Advisor//EN\nBEGIN:VEVENT\nUID:{uid}@cmu.edu\nDTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}\nDTSTART:{start_dt.strftime('%Y%m%dT%H%M%S')}\nDTEND:{end_dt.strftime('%Y%m%dT%H%M%S')}\nSUMMARY:{course['title']} ({course['course_id']})\nLOCATION:{course['location']}\nDESCRIPTION:{course['reason']}\nRRULE:FREQ=WEEKLY;COUNT=15;BYDAY={days[course['day']]}\nEND:VEVENT\nEND:VCALENDAR"""

# Recommendation Button
if st.button("✨ Recommend Courses"):
    with st.spinner("Analyzing your profile..."):
        recs = mock_recommendations(interests, resume, past_courses, hours_per_week, course_rating)
        if recs:
            for rec in recs:
                with st.chat_message("assistant"):
                    st.markdown(f"**{rec['title']} ({rec['course_id']})**")
                    st.write(rec['reason'])
                    st.write(f"**When & Where:** {rec['day']} {rec['start']}-{rec['end']} at {rec['location']}")
                    st.write(f"**Rating:** {rec['rating']}")
                    ics_file = create_ics(rec)
                    st.download_button(
                        label="📅 Add to Calendar (.ics)",
                        data=ics_file,
                        file_name=f"{rec['course_id']}.ics",
                        mime="text/calendar"
                    )
        else:
            st.chat_message("assistant").warning("Couldn't find courses matching your criteria. Try adjusting your preferences!")


