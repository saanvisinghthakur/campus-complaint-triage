# Campus Complaint Triage

An AI-powered complaint triage system for campuses, built using FastAPI and the Gemini API.

## Live Links
- 🔗 **Student Portal:** https://campus-complaint-triage.onrender.com/
- 🔗 **Admin Dashboard:** https://campus-complaint-triage.onrender.com/admin

> Note: hosted on Render's free tier, so it may take ~30 seconds to load if the site hasn't been visited recently.

## What it does
Students submit complaints through the portal with their name, roll number, and email. Each complaint is automatically classified by category and urgency using the Gemini API, and the student receives a unique tracking ID to check status later — no login required. Admins review, prioritize, and respond to complaints through a separate dashboard, with AI-drafted replies and live status tracking that syncs back to the student instantly.

## Features
- Student complaint form with name, roll number, and email — unique Complaint ID for tracking, no login required
- AI-powered classification: category, urgency level, and one-line summary (Gemini API)
- Clear submission confirmation with tracking ID
- Admin dashboard with sortable complaints table and color-coded urgency badges
- Status updates (Pending / In Progress / Resolved) that sync instantly to the student's tracking view
- AI-drafted reply suggestions, editable by admin before sending, visible to students on their tracking page
- Similarity-based repeated-complaint detection — flags likely duplicate issues reported by the same or different students
- Live stats chart showing complaint breakdown by category

## Tech Stack
Python · FastAPI · SQLite · Gemini API (gemini-3.5-flash-lite) · HTML/CSS/JS · Chart.js

## Deployment
Hosted on Render (free tier), deployed directly from this GitHub repository.

## Future Scope
- Unified single-entry portal with role-based access — a dropdown lets users select their role (Student, Faculty, Staff, Admin) before entering credentials, routing them to the appropriate view instead of relying on separate links
- Photo/image upload for complaints
- Email notifications on status updates or replies
- Full student login to view complaint history
- Public complaint feed — students can browse already-submitted complaints (anonymized) before submitting, to avoid duplicates and see what's already being addressed
- Semantic (AI-based) duplicate detection
- Multi-language complaint support
- Admin analytics dashboard (trends, resolution time, hotspots)
- Anonymous complaint option for sensitive cases