import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
from src.analysis import analyze_video, demo_session
from src.storage import init_db, save_session, load_sessions, load_attendance

st.set_page_config(page_title="Classroom Intelligence Agent", page_icon="🎓", layout="wide")
ROOT = Path(__file__).parent
init_db(ROOT / "data" / "classroom.db")

st.markdown("""
<style>
.main {background:#f6f8fc}
[data-testid="stMetric"] {background:white;padding:16px;border-radius:14px;border:1px solid #e8edf5}
.hero {padding:24px;border-radius:18px;background:linear-gradient(120deg,#172554,#2563eb);color:white;margin-bottom:18px}
.small-note {color:#5b6475;font-size:0.9rem}
</style>
<div class="hero"><h1>🎓 Classroom Intelligence Agent</h1>
<p>Offline-first attendance, session signals, and teaching recommendations</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Session setup")
    class_name = st.text_input("Class / course", "CSE - Classroom Demo")
    instructor = st.text_input("Instructor (optional)", "")
    st.caption("Media is processed locally by this app. Do not upload recordings without appropriate consent.")
    page = st.radio("Navigate", ["Dashboard", "Analyze a video", "Session history", "About & privacy"])

if page == "Dashboard":
    sessions = load_sessions(ROOT / "data" / "classroom.db")
    attendance = load_attendance(ROOT / "data" / "classroom.db")
    c1,c2,c3 = st.columns(3)
    c1.metric("Sessions analyzed", len(sessions))
    c2.metric("Attendance records", len(attendance))
    avg = round(pd.to_numeric(pd.DataFrame(sessions).get("engagement_proxy", pd.Series(dtype=float)), errors="coerce").mean(),1) if sessions else 0
    c3.metric("Avg. activity proxy", f"{avg}%" if pd.notna(avg) else "—")
    st.subheader("Recent sessions")
    if sessions:
        df = pd.DataFrame(sessions)
        st.dataframe(df[["created_at","class_name","source_name","duration_seconds","people_detected","engagement_proxy"]].tail(10), use_container_width=True, hide_index=True)
    else:
        st.info("No sessions yet. Open **Analyze a video** or load a demo session below.")
    if st.button("Load a sample demo session"):
        demo = demo_session(class_name)
        save_session(ROOT / "data" / "classroom.db", demo, [])
        st.success("Demo session added. This is synthetic sample data, not real attendance.")
        st.rerun()

elif page == "Analyze a video":
    st.subheader("Analyze classroom video")
    st.write("Upload an MP4, MOV, or AVI recording. Processing stays on this machine. A webcam/live mode can be added later.")
    uploaded = st.file_uploader("Choose classroom video", type=["mp4","mov","avi","mkv"])
    min_presence = st.slider("Minimum sustained detection (seconds)", 1, 30, 5)
    sample_every = st.slider("Analyze every Nth frame (higher is faster)", 1, 15, 5)
    if uploaded and st.button("Analyze session", type="primary"):
        temp_path = ROOT / "data" / f"upload_{uploaded.name.replace(' ','_')}"
        temp_path.write_bytes(uploaded.getvalue())
        with st.spinner("Processing video locally..."):
            try:
                result, timeline, attendance_rows = analyze_video(
                    str(temp_path), class_name, uploaded.name,
                    min_presence_seconds=min_presence, sample_every=sample_every
                )
                save_session(ROOT / "data" / "classroom.db", result, attendance_rows)
                st.success("Analysis complete.")
                st.session_state["last_result"] = result
                st.session_state["last_timeline"] = timeline
                st.session_state["last_attendance"] = attendance_rows
            except Exception as e:
                st.error(f"Could not analyze this video: {e}")
            finally:
                try: temp_path.unlink(missing_ok=True)
                except Exception: pass
    if "last_result" in st.session_state:
        r = st.session_state["last_result"]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Duration", f"{r['duration_seconds']} sec")
        c2.metric("People detected", r["people_detected"])
        c3.metric("Activity proxy", f"{r['engagement_proxy']}%")
        c4.metric("Sustained tracks", len(st.session_state["last_attendance"]))
        st.caption("These are computer-vision detections, not verified identities. Similar-looking or overlapping faces may be missed or counted inconsistently.")
        tl = pd.DataFrame(st.session_state["last_timeline"])
        if not tl.empty:
            st.plotly_chart(px.line(tl, x="time_seconds", y=["people_detected","movement_proxy"], title="Session signals over time"), use_container_width=True)
        st.subheader("Attendance-like detections")
        adf = pd.DataFrame(st.session_state["last_attendance"])
        st.dataframe(adf, use_container_width=True, hide_index=True)
        st.download_button("Download attendance CSV", adf.to_csv(index=False), "attendance_detections.csv", "text/csv")
        st.subheader("Agent recommendations")
        for tip in r["suggestions"]:
            st.write("• " + tip)
        st.warning("Engagement is represented by observable activity proxies only. The system cannot reliably infer a student's attention, understanding, emotion, or learning.")

elif page == "Session history":
    st.subheader("Saved session history")
    sessions = load_sessions(ROOT / "data" / "classroom.db")
    if sessions:
        df = pd.DataFrame(sessions)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Export session history CSV", df.to_csv(index=False), "session_history.csv", "text/csv")
    else:
        st.info("No saved sessions yet.")

else:
    st.subheader("Project scope")
    st.markdown("""
**Current MVP features**
- Local video upload and frame sampling
- OpenCV face detection and short-term detection tracking
- Timestamped detection logs based on sustained presence
- Movement/activity proxy and session timeline
- Rule-based teaching suggestions
- SQLite session history and CSV export

**Privacy and responsible use**
- No face recognition or identity matching is performed.
- Detection IDs are temporary track labels, not student names.
- Obtain consent and follow institutional policy before recording.
- Do not use activity proxies to grade students, punish them, or make high-stakes decisions.
- Delete recordings after analysis; the app stores session summaries, not uploaded videos.

**Limitations**
- Occlusion, camera angle, lighting, masks, and crowded rooms affect detection.
- The current version analyzes video only; audio activity and live webcam processing are planned extensions.
- Install model/package dependencies before disconnecting from the internet.
""")
