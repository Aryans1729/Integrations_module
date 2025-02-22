# Integrations_module
HubSpot, Notion &amp; Airtable Integration with FastAPI This project enables seamless integrationpot, Notion, and Airtable using FastAPI on the backend and a React-based frontend. The integration follows an OAuth 2.0 authentication flow, allowing users to connect their accounts and fetch relevant data from these platforms. 

HubSpot, Notion & Airtable Integration with FastAPI
This project integrates HubSpot, Notion, and Airtable using FastAPI on the backend and a React-based frontend. It supports OAuth 2.0 authentication, allowing users to securely connect their accounts and retrieve data.

Features
✅ OAuth Authentication – Secure login for HubSpot, Notion, and Airtable
✅ Data Retrieval – Fetch integration-specific data from each platform
✅ React Frontend – User-friendly interface to manage connections
✅ FastAPI Backend – Handles authentication, token storage, and API requests
✅ Redis for Caching – Enhances performance and efficiency

Setup & Installation
Prerequisites
Make sure you have the following installed:

Python 3.8+
Node.js & npm
Redis (for caching)
Backend Setup
Navigate to the backend directory:
bash
Copy
Edit
cd backend
Create and activate a virtual environment:
bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
Install dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Start the Redis server:
bash
Copy
Edit
redis-server
Run the FastAPI server:
bash
Copy
Edit
uvicorn main:app --reload
Frontend Setup
Navigate to the frontend directory:
bash
Copy
Edit
cd frontend
Install dependencies:
bash
Copy
Edit
npm install
Start the frontend server:
bash
Copy
Edit
npm run start
API Endpoints
HubSpot Integration
POST /integrations/hubspot/authorize – Initiates OAuth authentication
GET /integrations/hubspot/oauth2callback – Handles OAuth callback
POST /integrations/hubspot/credentials – Fetches stored credentials
POST /integrations/hubspot/load – Retrieves HubSpot data
Notion & Airtable
(Similar endpoints exist for Notion & Airtable, following the same structure.)

Contributing
Feel free to open issues and contribute improvements! 🚀

