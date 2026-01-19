from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import chat

app = FastAPI(
    title="Cyberpunk AI Chat Backend",
    description="Backend for a cyberpunk-themed AI chat application.",
    version="0.1.0",
)

# Configure CORS
# In a production environment, you should restrict origins to your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Cyberpunk AI Chat API!"}
