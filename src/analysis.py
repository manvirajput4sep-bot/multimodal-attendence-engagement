import cv2
import numpy as np
from datetime import datetime

def recommendations(activity, movement, people):
    tips = []
    if activity < 25:
        tips.append("Activity signals were low for this session. Consider a quick poll, recap question, or short pair discussion.")
    elif activity < 55:
        tips.append("Activity signals were moderate. Try adding a brief knowledge check midway through the next session.")
    else:
        tips.append("Movement/activity signals were relatively high. Review the timeline to distinguish productive interaction from general movement.")
    if movement < 8:
        tips.append("The sampled frames showed little visual change. Consider checking whether the camera view captures the whole class.")
    if people == 0:
        tips.append("No faces were detected reliably. Check camera placement, lighting, resolution, and whether participants face the camera.")
    tips.append("Treat these as prompts for instructor reflection, not as objective measurements of attention or learning.")
    return tips

def analyze_video(path, class_name, source_name, min_presence_seconds=5, sample_every=5):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError("Video file could not be opened.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = max(0, int(frame_count / fps)) if frame_count else 0
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_detector = cv2.CascadeClassifier(cascade_path)
    if face_detector.empty():
        cap.release()
        raise RuntimeError("OpenCV face detector could not be loaded.")
    timeline, detection_counts, gray_means = [], [], []
    frame_idx, sampled = 0, 0
    previous_gray = None
    while True:
        ok, frame = cap.read()
        if not ok: break
        if frame_idx % max(1, sample_every) == 0:
            h, w = frame.shape[:2]
            scale = min(1.0, 720 / max(w, h))
            if scale < 1:
                frame = cv2.resize(frame, (int(w*scale), int(h*scale)))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(28,28))
            count = len(faces)
            movement = 0.0
            if previous_gray is not None and previous_gray.shape == gray.shape:
                diff = cv2.absdiff(gray, previous_gray)
                movement = float(np.mean(diff))
            previous_gray = gray
            t = frame_idx / fps
            detection_counts.append(count)
            gray_means.append(movement)
            timeline.append({"time_seconds": round(t,1), "people_detected": count, "movement_proxy": round(movement,2)})
            sampled += 1
        frame_idx += 1
    cap.release()
    if sampled == 0:
        raise ValueError("No video frames were readable.")
    # Aggregate repeated face detections into conservative temporary track slots.
    # This is not identity tracking; it estimates sustained detections at session level.
    max_people = int(max(detection_counts, default=0))
    avg_people = float(np.mean(detection_counts))
    sustained = max(0, min(max_people, int(round(avg_people))))
    min_samples = max(1, int(min_presence_seconds * fps / max(1, sample_every)))
    rows = []
    for i in range(sustained):
        seen = sum(1 for c in detection_counts if c > i)
        seconds = seen * sample_every / fps
        if seconds >= min_presence_seconds:
            rows.append({
                "detection_id": f"Detection-{i+1:02d}",
                "first_seen_seconds": 0,
                "last_seen_seconds": round(duration,1),
                "detected_sample_seconds": round(seconds,1),
                "status": "Review required"
            })
    activity = int(max(0, min(100, round((np.mean(detection_counts) / max(1, max_people))*100)))) if max_people else 0
    movement_avg = float(np.mean(gray_means)) if gray_means else 0
    # Combined proxy is deliberately descriptive, not a validated attention score.
    movement_score = min(100, movement_avg * 2.5)
    engagement = int(round(0.6 * activity + 0.4 * movement_score))
    result = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "class_name": class_name,
        "source_name": source_name,
        "duration_seconds": duration,
        "people_detected": max_people,
        "engagement_proxy": engagement,
        "suggestions": recommendations(engagement, movement_avg, max_people)
    }
    return result, timeline, rows

def demo_session(class_name):
    return {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "class_name": class_name,
        "source_name": "synthetic_demo_data",
        "duration_seconds": 50,
        "people_detected": 24,
        "engagement_proxy": 62,
        "suggestions": recommendations(62, 11, 24)
    }
