# Cyberpunk AI Chat Application

A high-end, neon-styled Cyberpunk AI Chat application. This project features a React frontend with a message history sidebar and a Python FastAPI backend with a dedicated `/chat` endpoint for AI interactions.

## Features

*   **Neon-styled React Frontend**: Immerse yourself in a cyberpunk aesthetic with vibrant neon colors, glow effects, and futuristic UI elements.
*   **Message History Sidebar**: Easily navigate through past conversations and pick up where you left off.
*   **Chat Interface**: A sleek and intuitive chat interface for seamless communication with the AI.
*   **Python FastAPI Backend**: A robust and high-performance backend serving the chat functionalities.
*   **/chat Endpoint**: A dedicated API endpoint for processing user messages and generating AI responses.
*   **CORS Middleware**: Properly configured for frontend-backend communication.
*   **Modular Architecture**: Designed for scalability and easy future enhancements.

## Technology Stack

### Frontend
*   **Framework**: React 18+ with Vite
*   **Language**: JavaScript/JSX
*   **Styling**: CSS3 with CSS Variables (Cyberpunk theme)
*   **HTTP Client**: Fetch API / Axios (or similar)
*   **State Management**: React Hooks

### Backend
*   **Framework**: FastAPI (Python 3.9+)
*   **ASGI Server**: Uvicorn
*   **CORS**: FastAPI CORS Middleware
*   **Serialization**: Pydantic

## Architecture Overview

The application follows a Client-Server architecture with a RESTful API.

```
┌─────────────────────────────────────┐
│     React Frontend (Client)         │
│  - Cyberpunk UI Components          │
│  - Message History Sidebar          │
│  - Chat Interface                   │
│  - Neon Styling & Animations        │
└──────────────┬──────────────────────┘
               │ HTTP/REST
               │ (JSON)
┌──────────────▼──────────────────────┐
│   FastAPI Backend (Server)          │
│  - /chat endpoint                   │
│  - Message processing               │
│  - CORS middleware                  │
│  - AI integration layer             │
└─────────────────────────────────────┘
```

For a more detailed architecture, refer to `docs/architecture.md`.

## Directory Structure

```
cyberpunk-ai-chat/
├── docs/
│   ├── architecture.md
│   ├── interfaces.md
│   └── setup.md
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   └── chat.py
│   │   └── services/
│   │       └── ai_service.py
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

## Setup and Installation

Please follow the detailed instructions in `docs/setup.md` to get the application up and running.

### Quick Start (Summary)

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd cyberpunk-ai-chat
    ```
2.  **Backend Setup**:
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env # Configure your .env file
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    (Backend will be accessible at `http://localhost:8000`)
3.  **Frontend Setup**:
    ```bash
    cd ../frontend
    npm install
    echo "VITE_API_BASE_URL=http://localhost:8000" > .env # Configure your .env file
    npm run dev
    ```
    (Frontend will be accessible at `http://localhost:5173`)

## Usage

Once both the frontend and backend servers are running:
1.  Open your web browser and navigate to `http://localhost:5173`.
2.  Type your message into the input box at the bottom of the chat interface.
3.  Press Enter or click the "Send" button.
4.  Observe the AI's neon-themed response and interaction.
5.  Check the message history sidebar for your conversation flow.

## API Endpoints

### Backend API
The backend exposes the following primary endpoints:

*   **POST `/chat`**: Process a chat message and return an AI response.
    *   **Request Body**:
        ```json
        {
          "message": "string"
        }
        ```
    *   **Response Body**:
        ```json
        {
          "response": "string",
          "sent_message": "string"
        }
        ```
*   **GET `/`**: Health check / Welcome message.

For detailed API interfaces, including models and potential future enhancements like `conversation_id` and `timestamp`, please refer to `docs/interfaces.md`.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details (if applicable).
