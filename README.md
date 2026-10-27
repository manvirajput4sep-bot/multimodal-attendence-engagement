#
 Multimodal Attendance & Engagement Agent — MVP

An offline-first classroom analytics prototype built with Python, Streamlit, OpenCV, SQLite, Pandas, and Plotly.

## Features
- Upload and locally process classroom video
- Detect faces in sampled frames using OpenCV
- Estimate sustained detection slots (not verified identities)
- Plot detected-person counts and visual movement proxy over time
- Generate rule-based teaching suggestions
- Save session summaries to SQLite and export CSV

## Important limitations
This is a prototype, not a validated attendance or engagement measurement system. The current version does not recognize student identities, does not perform robust multi-object tracking, and does not process audio. Its "engagement proxy" is a simple combination of visible detections and frame-to-frame visual change; it is not a measure of attention, understanding, emotion, or learning. Human review is required.

## Requirements
- Python 3.10+
- Windows 10/11, macOS, or Linux
- Webcam not required for the current video-upload version
- Internet is needed for initial package installation; after packages are installed, analysis can run locally

## Run on Windows
1. Extract the ZIP.
2. Open the project folder in VS Code.
3. Open Terminal in that folder.
4. Create a virtual environment:
   ```bash
   py -m venv .venv
   .venv\\Scripts\\activate
   ```
5. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
6. Start the app:
   ```bash
   streamlit run app.py
   ```
7. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Run on macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```text
Multimodal_Attendance_Engagement_Agent/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── .gitkeep
└── src/
    ├── __init__.py
    ├── analysis.py
    └── storage.py
```

## Next development milestones
1. Add robust multi-object tracking (e.g., YOLO + ByteTrack) and human-reviewed attendance identity mapping.
2. Add local audio activity detection without speech transcription by default.
3. Add configurable, explainable engagement indicators and instructor feedback.
4. Add role-based instructor/student views and consent-aware retention controls.
5. Add tests, packaging, and a documented offline installation bundle.

## Privacy checklist
- Obtain consent and follow institutional policy before recording.
- Prefer local processing and minimal data retention.
- Do not infer sensitive traits or use the score for grading, discipline, or other high-stakes decisions.
- Delete source recordings after processing.

