# Integrations Module  
### HubSpot, Notion & Airtable Integration with FastAPI  

This project provides seamless integration with **HubSpot, Notion, and Airtable**, using a **FastAPI backend** and a **React-based frontend**. It follows the **OAuth 2.0 authentication flow**, allowing users to securely connect their accounts and retrieve relevant data from these platforms.

---

## Features  

- ✅ **OAuth 2.0 Authentication** – Secure login for HubSpot, Notion, and Airtable  
- ✅ **Data Retrieval** – Fetch platform-specific data  
- ✅ **React Frontend** – User-friendly UI for managing integrations  
- ✅ **FastAPI Backend** – Handles authentication, token storage, and API requests  
- ✅ **Redis Caching** – Enhances performance and efficiency  

---

## Getting Started  

### Prerequisites  
Ensure you have the following installed:  

- **Python 3.8+**  
- **Node.js & npm**  
- **Redis** (for caching)  

---

### Backend Setup  

1. Navigate to the backend directory:  
2. Create and activate a virtual environment:  
- **macOS/Linux**:  
  ```
  python -m venv venv
  source venv/bin/activate
  ```
- **Windows**:  
  ```
  python -m venv venv
  venv\Scripts\activate
  ```
3. Install dependencies:  
pip install -r requirements.txt

4. Start the Redis server:  
redis-server

5. Run the FastAPI server:  
uvicorn main:app --reload


---

### Frontend Setup  

1. Navigate to the frontend directory:  
cd frontend

markdown
Copy
Edit
2. Install dependencies:  
npm install

markdown
Copy
Edit
3. Start the frontend server:  
npm run start

yaml
Copy
Edit

---

## API Endpoints  

### HubSpot Integration  
- `POST /integrations/hubspot/authorize` – Initiates OAuth authentication  
- `GET /integrations/hubspot/oauth2callback` – Handles OAuth callback  
- `POST /integrations/hubspot/credentials` – Retrieves stored credentials  
- `POST /integrations/hubspot/load` – Fetches data from HubSpot  

### Notion & Airtable Integration  
- Similar endpoints exist for Notion & Airtable, following the same authentication flow.  

---

## Contributing  

Contributions are welcome! Feel free to open issues or submit pull requests. 🚀  

---
