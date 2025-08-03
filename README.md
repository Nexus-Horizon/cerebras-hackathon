# AI Assistant - Full Stack Application

This is a full-stack AI assistant application with a Next.js frontend and FastAPI backend.

## Project Structure

```
├── frontend/          # Next.js frontend application
└── backend/           # FastAPI backend application
```

## Frontend (Next.js + TypeScript)

### Features
- Image upload (JPG/PNG)
- Question input field
- Form submission to backend
- Axios for API communication

### Setup and Run

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Backend (FastAPI + Python)

### Features
- FastAPI server on port 8000
- Image upload endpoint (`/analyze`)
- CORS enabled for localhost:3000
- File validation and storage
- Latency measurement

### Setup and Run

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   python run.py
   ```
   Or on Windows, you can simply double-click `start.bat`

5. The API will be available at [http://localhost:8000](http://localhost:8000)

### Alternative Setup (Windows)
- Double-click `backend/start.bat` to start the server

## API Endpoints

### Frontend
- `GET /` - Main page with upload form

### Backend
- `GET /` - Health check endpoint
- `POST /analyze` - Image analysis endpoint
  - Form fields:
    - `question` (string)
    - `image` (file upload)
  - Response:
    ```json
    {
      "task": "To be classified",
      "question": "User's question",
      "filename": "uploaded_image.jpg",
      "latency": 0.1234
    }
    ```

## Development

### Frontend Components
- `pages/index.tsx` - Main page with image upload form
- Uses React hooks for state management
- Axios for HTTP requests

### Backend Components
- `app/main.py` - Main FastAPI application
- `app/routers/analyze.py` - Image analysis router
- `uploads/` - Directory for uploaded images

## Testing the Application

1. Start the backend server first
2. Start the frontend development server
3. Navigate to http://localhost:3000
4. Upload an image and ask a question
5. Check the backend console for logged information
6. Check the browser console for the response
