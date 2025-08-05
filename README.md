CSV Filter Tool - Streamlit + FastAPI
Overview
This application provides a powerful CSV filtering solution that combines Streamlit's user-friendly interface with a FastAPI backend for handling large files. The system automatically determines whether to process files locally (for small files <200MB) or send them to a cloud backend (for larger files).

Features
Dual Processing Mode:

Small files (<200MB) processed directly in Streamlit

Large files automatically sent to FastAPI backend

Advanced Filtering:

Multiple filter conditions

Exact or contains matching

Regex support

Wildcard support (*)

Preview & Download:

View filtered results preview

Download full filtered dataset

System Architecture
text
Streamlit Frontend (UI) ↔ FastAPI Backend (Processing)
Setup Instructions
Prerequisites
Python 3.8+

Streamlit

FastAPI (for backend)

Pandas

Installation
Clone the repository:

bash
git clone [your-repository-url]
cd [your-project-directory]
Set up virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install streamlit pandas requests fastapi uvicorn python-multipart
Configuration
Backend URL:

Open filter-data.py

Locate the BACKEND_URL variable near the top

Replace with your FastAPI backend URL:

python
BACKEND_URL = "http://your-backend-ip:8000"  # Or your domain
Environment Variables (Optional):

For production, consider using environment variables for configuration:

python
import os
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
Running the Application
Development Mode
Run Streamlit frontend:

bash
streamlit run filter-data.py
Run FastAPI backend (in separate terminal):

bash
uvicorn backend:app --reload
Production Deployment
Backend:

Deploy backend.py using:

Gunicorn + Uvicorn for production

Nginx as reverse proxy

Configure SSL

Frontend:

Deploy to Streamlit Sharing

Or host using Streamlit in production mode

Usage Guide
Upload a CSV file:

Drag and drop or click to browse

System automatically detects file size

Configure filters:

Check if file has headers

Select match type (exact or contains)

Add filter conditions:

Select column

Enter value

Use [value] for exact match in contains mode

Use * as wildcard

View results:

Preview shows first 5 matching rows

Download full results as CSV

Troubleshooting
Common Issues
Connection to backend fails:

Verify backend is running

Check BACKEND_URL is correct

Ensure no firewall blocking ports

Large file processing errors:

Check backend server has enough memory

Consider increasing timeout in requests

Encoding issues:

Try different file encodings

Ensure consistent encoding between files

License
[Specify your license here]

Support
For issues or questions, please contact [your contact information]
