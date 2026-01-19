# Cyberpunk AI Chat - Setup Guide

## Prerequisites

### Required Software
- **Node.js**: v18.0.0 or higher
- **Python**: 3.9 or higher
- **npm** or **yarn**: Latest version
- **pip**: Latest version

### Recommended Tools
- **VS Code** or any modern code editor
- **Git**: For version control
- **Postman** or **curl**: For API testing

---

## Installation

### 1. Clone or Setup Project
```bash
# If cloning from repository
git clone <repository-url>
cd cyberpunk-ai-chat

# Or create the directory structure manually
mkdir cyberpunk-ai-chat
cd cyberpunk-ai-chat
```

### 2. Backend Setup

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# CORS_ORIGINS=http://localhost:5173
# PORT=8000
```

#### Run Backend Server
```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Navigate to Frontend Directory
```bash
# Open a new terminal
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Configure Environment Variables
```bash
# Create .env file in frontend directory
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
```

#### Run Frontend Development Server
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## Project Structure

```
cyberpunk-ai-chat/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # Pydantic models
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # Chat endpoint routes
│   │   └── services/
│   │       ├── __init__.py
│   │       └── ai_service.py    # AI response generation
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── styles/            # CSS stylesheets
│   │   ├── services/          # API services
│   │   ├── App.jsx            # Main App component
│   │   └── main.jsx           # Application entry point
│   ├── package.json           # Node dependencies
│   └── vite.config.js         # Vite configuration
└── docs/
    ├── architecture.md        # System architecture
    ├── interfaces.md          # API and component interfaces
    └── setup.md              # This file
```

---

## Development Workflow

### Starting the Application

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Testing the Application

#### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, AI!"}'
```

#### Test Frontend
- Open browser to http://localhost:5173
- Type a message in the input box
- Click send or press Enter
- Verify message appears in chat and AI responds

---

## Build for Production

### Backend Production Build

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend Production Build

```bash
cd frontend

# Build optimized production bundle
npm run build

# Preview production build
npm run preview

# Output will be in: frontend/dist/
```

### Deployment Options

#### Option 1: Static Hosting (Frontend)
- Deploy `frontend/dist/` to:
  - Vercel
  - Netlify
  - AWS S3 + CloudFront
  - GitHub Pages

#### Option 2: Backend Hosting
- Deploy backend to:
  - Heroku
  - AWS EC2/ECS
  - Google Cloud Run
  - DigitalOcean App Platform

#### Option 3: Full Stack Deployment
- Use Docker containers
- Deploy to Kubernetes
- Use Platform-as-a-Service (PaaS) solutions

---

## Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Check if port 8000 is in use
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000
```

#### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

#### CORS Errors
- Verify backend CORS_ORIGINS in .env includes frontend URL
- Check that backend is running on correct port
- Ensure frontend API_BASE_URL matches backend URL

#### API Connection Failed
- Verify backend is running: http://localhost:8000/health
- Check frontend .env file has correct VITE_API_BASE_URL
- Check browser console for detailed error messages

---

## Environment Variables Reference

### Backend (.env)
```env
# Server Configuration
PORT=8000
HOST=0.0.0.0

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Application Settings
DEBUG=True
AI_MODEL=gpt-simulation
```

### Frontend (.env)
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Application Settings
VITE_APP_TITLE=Cyberpunk AI Chat
```

---

## Useful Commands

### Backend
```bash
# Run with auto-reload (development)
uvicorn app.main:app --reload

# Run on specific port
uvicorn app.main:app --port 8080

# View API documentation
# Navigate to http://localhost:8000/docs
```

### Frontend
```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## Next Steps

1. **Customize the UI**: Modify cyberpunk theme colors in `frontend/src/styles/cyberpunk.css`
2. **Add Features**: Extend chat functionality with new components
3. **Integrate Real AI**: Replace mock AI service with actual AI API (OpenAI, Anthropic, etc.)
4. **Add Persistence**: Integrate database for message storage
5. **Implement Auth**: Add user authentication and authorization

---

## Support & Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Vite Documentation**: https://vitejs.dev/

---

## License

This project is provided as-is for educational and commercial use.
