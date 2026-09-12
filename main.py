from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() #reads your .env file so the code can use your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
model = genai.GenerativeModel("gemini-3.6-flash")

# Set up the database (creates the file/table if they don't exist yet)
def init_db():   #creates a small database file called complaints.db with a table to store complaints
    conn = sqlite3.connect("complaints.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            category TEXT,
            urgency TEXT,
            summary TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

class Complaint(BaseModel):
    text: str

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/admin")
def read_admin():
    return FileResponse("static/admin.html")

@app.post("/classify")  #now saves the result and sends back a simple confirmation message 
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
    result_text = response.text

    # Pull out each line from Gemini's reply
    lines = result_text.strip().split("\n")
    category = lines[0].replace("Category:", "").strip()
    urgency = lines[1].replace("Urgency:", "").strip()
    summary = lines[2].replace("Summary:", "").strip()

    # Save it to the database
    conn = sqlite3.connect("complaints.db")
    conn.execute(
        "INSERT INTO complaints (text, category, urgency, summary, created_at) VALUES (?, ?, ?, ?, ?)",
        (complaint.text, category, urgency, summary, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return {"message": "Your complaint has been submitted and will be reviewed."}

@app.get("/complaints")  #address returns all saved complaints as data (this is what the admin page will read)
def get_complaints():
    conn = sqlite3.connect("complaints.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]