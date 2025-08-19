#!/usr/bin/env python3
"""
FastAPI Server for Core Assistant Pipeline
Exposes email tools as HTTP endpoints for AIXPLAIN Email Agent
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import existing email tools
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids

load_dotenv()

app = FastAPI(
    title="Core Assistant API",
    description="API server for Core Assistant Pipeline - Email Tools",
    version="1.0.0"
)

# Request models
class EmailDateRangeRequest(BaseModel):
    start_date: str
    end_date: str
    user_id: Optional[str] = None

class EmailSenderRequest(BaseModel):
    sender: str
    date: str
    user_id: Optional[str] = None

class EmailSubjectRequest(BaseModel):
    subject: str
    start_date: str
    end_date: str
    user_id: Optional[str] = None

class EmailIdsRequest(BaseModel):
    email_ids: List[str]
    user_id: Optional[str] = None

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Core Assistant API Server",
        "version": "1.0.0",
        "status": "running",
        "services": ["email_tools"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Core Assistant API"}

# Email endpoints
@app.post("/email/by-date-range")
async def email_by_date_range(request: EmailDateRangeRequest):
    """
    Retrieve emails within a specific date range
    """
    try:
        # Use default user_id if not provided
        user_id = request.user_id or os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        
        result = retrieve_emails_by_date_range(
            request.start_date, 
            request.end_date, 
            user_id=user_id
        )
        
        return {
            "success": True,
            "count": result.get('count', 0),
            "summary": result.get('summary', ''),
            "items": result.get('items', []),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving emails by date range: {str(e)}"
        )

@app.post("/email/by-sender-date")
async def email_by_sender_date(request: EmailSenderRequest):
    """
    Find emails from a specific sender on a specific date
    """
    try:
        # Use default user_id if not provided
        user_id = request.user_id or os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        
        result = retrieve_emails_by_sender_date(
            request.sender, 
            request.date, 
            user_id=user_id
        )
        
        return {
            "success": True,
            "count": result.get('count', 0),
            "summary": result.get('summary', ''),
            "items": result.get('items', []),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving emails by sender and date: {str(e)}"
        )

@app.post("/email/by-subject-date-range")
async def email_by_subject_date_range(request: EmailSubjectRequest):
    """
    Search emails by subject keyword within date range
    """
    try:
        # Use default user_id if not provided
        user_id = request.user_id or os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        
        result = retrieve_emails_by_subject_date_range(
            request.subject, 
            request.start_date, 
            request.end_date, 
            user_id=user_id
        )
        
        return {
            "success": True,
            "count": result.get('count', 0),
            "summary": result.get('summary', ''),
            "items": result.get('items', []),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving emails by subject and date range: {str(e)}"
        )

@app.post("/email/by-ids")
async def email_by_ids(request: EmailIdsRequest):
    """
    Retrieve specific emails by their IDs
    """
    try:
        # Use default user_id if not provided
        user_id = request.user_id or os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        
        result = retrieve_emails_by_ids(
            request.email_ids, 
            user_id=user_id
        )
        
        return {
            "success": True,
            "count": result.get('count', 0),
            "summary": result.get('summary', ''),
            "items": result.get('items', []),
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving emails by IDs: {str(e)}"
        )

@app.get("/email/cached-ids")
async def get_cached_email_ids_endpoint():
    """
    Get cached email IDs for quick access
    """
    try:
        cached_ids = get_cached_email_ids()
        return {
            "success": True,
            "count": len(cached_ids),
            "email_ids": cached_ids,
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving cached email IDs: {str(e)}"
        )

@app.post("/email/refresh-cache")
async def refresh_email_cache():
    """
    Refresh the email ID cache
    """
    try:
        user_id = os.getenv('DEFAULT_USER_ID', 'executive.assistant@menadevs.io')
        fetch_last_email_ids(user_id)
        
        return {
            "success": True,
            "message": "Email cache refreshed successfully",
            "error": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error refreshing email cache: {str(e)}"
        )

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "success": False,
        "error": str(exc),
        "count": 0,
        "summary": "An error occurred while processing the request",
        "items": []
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    print(f"🚀 Starting Core Assistant API Server...")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📧 Email tools available:")
    print(f"   - POST /email/by-date-range")
    print(f"   - POST /email/by-sender-date")
    print(f"   - POST /email/by-subject-date-range")
    print(f"   - POST /email/by-ids")
    print(f"   - GET /email/cached-ids")
    print(f"   - POST /email/refresh-cache")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )
