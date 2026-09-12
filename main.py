from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
import sqlite3
import random
import string
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
model = genai.GenerativeModel("gemini-3.5-flash-lite")

def init_db():
    conn = sqlite3.connect("complaints.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_code TEXT UNIQUE,
            student_name TEXT,
            roll_number TEXT,
            email TEXT,
            text TEXT,
            category TEXT,
            urgency TEXT,
            summary TEXT,
            status TEXT DEFAULT 'Pending',
            reply TEXT DEFAULT '',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def generate_code():
    return "C" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

class Complaint(BaseModel):
    student_name: str
    roll_number: str
    email: str
    text: str

class StatusUpdate(BaseModel):
    status: str

class ReplyUpdate(BaseModel):
    reply: str

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/admin")
def read_admin():
    return FileResponse("static/admin.html")

@app.post("/classify")
def classify_complaint(complaint: Complaint):
    prompt = f"""
    You are helping triage campus complaints.
    Read this complaint and respond ONLY in this exact format, nothing else:

    Category: <one of: Maintenance, Food, Academic, Security, IT, Other>
    Urgency: <one of: Low, Medium, High>
    Summary: <one short sentence>

    Complaint: {complaint.text}
    """
    response = model.generate_content(prompt)
    lines = response.text.strip().split("\n")
    category = lines[0].replace("Category:", "").strip()
    urgency = lines[1].replace("Urgency:", "").strip()
    summary = lines[2].replace("Summary:", "").strip()
    code = generate_code()

    conn = sqlite3.connect("complaints.db")
    conn.execute(
        "INSERT INTO complaints (complaint_code, student_name, roll_number, email, text, category, urgency, summary, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (code, complaint.student_name, complaint.roll_number, complaint.email, complaint.text, category, urgency, summary, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return {"message": "Your complaint has been submitted.", "code": code}

@app.get("/track/{code}")
def track_complaint(code: str):
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM complaints WHERE complaint_code = ?", (code,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"error": "No complaint found with that ID."}

@app.get("/complaints")
def get_complaints():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.patch("/complaints/{complaint_id}/status")
def update_status(complaint_id: int, update: StatusUpdate):
    conn = sqlite3.connect("complaints.db")
    conn.execute("UPDATE complaints SET status = ? WHERE id = ?", (update.status, complaint_id))
    conn.commit()
    conn.close()
    return {"message": "Status updated."}

@app.patch("/complaints/{complaint_id}/reply")
def update_reply(complaint_id: int, update: ReplyUpdate):
    conn = sqlite3.connect("complaints.db")
    conn.execute("UPDATE complaints SET reply = ? WHERE id = ?", (update.reply, complaint_id))
    conn.commit()
    conn.close()
    return {"message": "Reply saved."}

@app.post("/draft-reply/{complaint_id}")
def draft_reply(complaint_id: int):
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    conn.close()
    if not row:
        return {"error": "Complaint not found."}

    prompt = f"""
    Write a short, polite reply (2-3 sentences) from campus admin staff to a student
    who submitted this complaint: "{row['text']}"
    Category: {row['category']}, Urgency: {row['urgency']}.
    The reply should acknowledge the issue and briefly state next steps.
    """
    response = model.generate_content(prompt)
    return {"draft": response.text.strip()}