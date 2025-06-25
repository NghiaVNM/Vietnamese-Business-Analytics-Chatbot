from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import engine, Base, get_db, test_db_connection
from app.api.endpoints import employees

# Test database connection khi start
print("Testing database connection...")
if test_db_connection():
    print("✅ Database connection successful!")
else:
    print("❌ Database connection failed!")

# Create database tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")

# Initialize FastAPI app
app = FastAPI(
    title="Employee Management API",
    description="API for Vietnamese Business Analytics Employee Management Demo",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    employees.router,
    prefix="/api/employees",
    tags=["employees"]
)

@app.get("/")
def read_root():
    return {"message": "Employee Management API is running with PostgreSQL!"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check with database connection test"""
    try:
        # Fix: sử dụng text() để wrap SQL
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "PostgreSQL connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }