from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()            #reads your .env file so the code can use your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()  #creates your web server
model = genai.GenerativeModel("gemini-3.6-flash")

class Complaint(BaseModel):
    text: str

@app.post("/classify")  #creates a web address (/classify) that accepts a complaint and returns Gemini's answer
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
    return {"result": response.text}