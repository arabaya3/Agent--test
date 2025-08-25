from flask import Flask, request, jsonify, render_template
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the email tools
from Email_Tools.email_by_sender import search_emails_by_sender
from Email_Tools.email_by_id import search_email_by_id
from Email_Tools.email_by_subject import search_emails_by_subject

# Import calendar tools
from Calender_Tools.calendar_api_wrappers import search_meetings_by_organizer_date, search_meetings_by_subject_date_range
from Calender_Tools.Calender_Date_Retriever import retrieve_meetings_by_date

# Import meeting tools
from meeting_tools.meeting_api_wrappers import get_meeting_by_id, get_meetings_by_title, get_meeting_attendance, get_meeting_audience, get_meeting_transcript

# Import OneDrive tools
from OneDrive_Tools.list_onedrive_files import list_onedrive_files
from OneDrive_Tools.onedrive_api_wrappers import list_shared_files, retrieve_file_by_name_with_folder

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint with web interface"""
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "message": "Core Pipeline API Server",
        "version": "2.0.0",
        "endpoints": {
            "Email Tools": {
                "/api/emails/sender/<sender>": {
                    "method": "GET",
                    "description": "Search emails by sender email or name",
                    "example": "/api/emails/sender/john@example.com"
                },
                "/api/emails/id/<email_id>": {
                    "method": "GET", 
                    "description": "Get detailed email information by ID",
                    "example": "/api/emails/id/AAMkAGI2TG93AAA="
                },
                "/api/emails/subject/<subject>": {
                    "method": "GET",
                    "description": "Search emails by subject line",
                    "example": "/api/emails/subject/meeting"
                },
                "/api/emails/search": {
                    "method": "POST",
                    "description": "Search emails with flexible parameters",
                    "body": {
                        "search_type": "sender|id|subject",
                        "query": "search term or email id"
                    }
                }
            },
            "Calendar Tools": {
                "/api/calendar/date/<date>": {
                    "method": "GET",
                    "description": "Get all meetings for a specific date",
                    "example": "/api/calendar/date/2024-01-15"
                },
                "/api/calendar/organizer/<organizer>/date/<date>": {
                    "method": "GET",
                    "description": "Search meetings by organizer and date",
                    "example": "/api/calendar/organizer/john@example.com/date/2024-01-15"
                },
                "/api/calendar/subject/<subject>/start/<start_date>/end/<end_date>": {
                    "method": "GET",
                    "description": "Search meetings by subject and date range",
                    "example": "/api/calendar/subject/meeting/start/2024-01-01/end/2024-01-31"
                }
            },
            "Meeting Tools": {
                "/api/meetings/id/<meeting_id>": {
                    "method": "GET",
                    "description": "Get meeting details by ID",
                    "example": "/api/meetings/id/123456789"
                },
                "/api/meetings/title/<title>": {
                    "method": "GET",
                    "description": "Search meetings by title",
                    "example": "/api/meetings/title/weekly"
                },
                "/api/meetings/attendance/<meeting_id>": {
                    "method": "GET",
                    "description": "Get meeting attendance information",
                    "example": "/api/meetings/attendance/123456789"
                },
                "/api/meetings/audience/<meeting_id>": {
                    "method": "GET",
                    "description": "Get meeting audience information",
                    "example": "/api/meetings/audience/123456789"
                },
                "/api/meetings/transcript/<meeting_id>": {
                    "method": "GET",
                    "description": "Get meeting transcript",
                    "example": "/api/meetings/transcript/123456789"
                }
            },
            "OneDrive Tools": {
                "/api/onedrive/files": {
                    "method": "GET",
                    "description": "List OneDrive files",
                    "query_params": {
                        "folder_path": "optional folder path",
                        "top": "number of files to return (default: 20)"
                    },
                    "example": "/api/onedrive/files?folder_path=Documents&top=10"
                },
                "/api/onedrive/shared": {
                    "method": "GET",
                    "description": "List shared files",
                    "query_params": {
                        "top": "number of files to return (default: 20)"
                    },
                    "example": "/api/onedrive/shared?top=10"
                },
                "/api/onedrive/file/<file_name>": {
                    "method": "GET",
                    "description": "Retrieve file by name",
                    "query_params": {
                        "folder_path": "optional folder path"
                    },
                    "example": "/api/onedrive/file/document.pdf?folder_path=Documents"
                }
            }
        }
    })

# Email endpoints (existing)
@app.route('/api/emails/sender/<sender>')
def api_search_by_sender(sender):
    """API endpoint to search emails by sender"""
    try:
        if not sender:
            return jsonify({"error": "Sender parameter is required"}), 400
        
        result = search_emails_by_sender(sender)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/emails/id/<email_id>')
def api_search_by_id(email_id):
    """API endpoint to get email details by ID"""
    try:
        if not email_id:
            return jsonify({"error": "Email ID parameter is required"}), 400
        
        result = search_email_by_id(email_id)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/emails/subject/<subject>')
def api_search_by_subject(subject):
    """API endpoint to search emails by subject"""
    try:
        if not subject:
            return jsonify({"error": "Subject parameter is required"}), 400
        
        result = search_emails_by_subject(subject)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/emails/search', methods=['POST'])
def api_search_emails():
    """Flexible search endpoint that accepts POST requests with search parameters"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        search_type = data.get('search_type', '').lower()
        query = data.get('query', '')
        
        if not search_type or not query:
            return jsonify({
                "error": "Both 'search_type' and 'query' are required in request body"
            }), 400
        
        if search_type not in ['sender', 'id', 'subject']:
            return jsonify({
                "error": "search_type must be one of: sender, id, subject"
            }), 400
        
        # Route to appropriate function based on search type
        if search_type == 'sender':
            result = search_emails_by_sender(query)
        elif search_type == 'id':
            result = search_email_by_id(query)
        elif search_type == 'subject':
            result = search_emails_by_subject(query)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Calendar endpoints
@app.route('/api/calendar/date/<date>')
def api_calendar_by_date(date):
    """API endpoint to get meetings by date"""
    try:
        if not date:
            return jsonify({"error": "Date parameter is required"}), 400
        
        result = retrieve_meetings_by_date(date)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/calendar/organizer/<organizer>/date/<date>')
def api_calendar_by_organizer_date(organizer, date):
    """API endpoint to search meetings by organizer and date"""
    try:
        if not organizer or not date:
            return jsonify({"error": "Both organizer and date parameters are required"}), 400
        
        result = search_meetings_by_organizer_date(organizer, date)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/calendar/subject/<subject>/start/<start_date>/end/<end_date>')
def api_calendar_by_subject_date_range(subject, start_date, end_date):
    """API endpoint to search meetings by subject and date range"""
    try:
        if not subject or not start_date or not end_date:
            return jsonify({"error": "Subject, start_date, and end_date parameters are required"}), 400
        
        result = search_meetings_by_subject_date_range(subject, start_date, end_date)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# Meeting endpoints
@app.route('/api/meetings/id/<meeting_id>')
def api_meeting_by_id(meeting_id):
    """API endpoint to get meeting details by ID"""
    try:
        if not meeting_id:
            return jsonify({"error": "Meeting ID parameter is required"}), 400
        
        result = get_meeting_by_id(meeting_id)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/meetings/title/<title>')
def api_meeting_by_title(title):
    """API endpoint to search meetings by title"""
    try:
        if not title:
            return jsonify({"error": "Title parameter is required"}), 400
        
        result = get_meetings_by_title(title)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/meetings/attendance/<meeting_id>')
def api_meeting_attendance(meeting_id):
    """API endpoint to get meeting attendance"""
    try:
        if not meeting_id:
            return jsonify({"error": "Meeting ID parameter is required"}), 400
        
        result = get_meeting_attendance(meeting_id)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/meetings/audience/<meeting_id>')
def api_meeting_audience(meeting_id):
    """API endpoint to get meeting audience"""
    try:
        if not meeting_id:
            return jsonify({"error": "Meeting ID parameter is required"}), 400
        
        result = get_meeting_audience(meeting_id)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/meetings/transcript/<meeting_id>')
def api_meeting_transcript(meeting_id):
    """API endpoint to get meeting transcript"""
    try:
        if not meeting_id:
            return jsonify({"error": "Meeting ID parameter is required"}), 400
        
        result = get_meeting_transcript(meeting_id)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

# OneDrive endpoints
@app.route('/api/onedrive/files')
def api_onedrive_files():
    """API endpoint to list OneDrive files"""
    try:
        folder_path = request.args.get('folder_path', '')
        top = request.args.get('top', 20, type=int)
        
        result = list_onedrive_files(folder_path, top)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/onedrive/shared')
def api_onedrive_shared():
    """API endpoint to list shared files"""
    try:
        top = request.args.get('top', 20, type=int)
        
        result = list_shared_files(top)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/onedrive/file/<file_name>')
def api_onedrive_file_by_name(file_name):
    """API endpoint to retrieve file by name"""
    try:
        if not file_name:
            return jsonify({"error": "File name parameter is required"}), 400
        
        folder_path = request.args.get('folder_path', '')
        
        result = retrieve_file_by_name_with_folder(file_name, folder_path)
        
        # Check if the result contains an error
        if result.startswith("ERROR:"):
            return jsonify({"error": result}), 500
        
        return jsonify({"result": result})
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Core Pipeline API is running"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ['TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET', 'DEFAULT_USER_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please make sure your .env file contains all required variables.")
        sys.exit(1)
    
    print("Starting Core Pipeline API Server...")
    print("Available endpoints:")
    print("  GET  /                    - Web interface")
    print("  GET  /api/docs            - API documentation")
    print("\nEmail Tools:")
    print("  GET  /api/emails/sender/<sender>")
    print("  GET  /api/emails/id/<email_id>")
    print("  GET  /api/emails/subject/<subject>")
    print("  POST /api/emails/search")
    print("\nCalendar Tools:")
    print("  GET  /api/calendar/date/<date>")
    print("  GET  /api/calendar/organizer/<organizer>/date/<date>")
    print("  GET  /api/calendar/subject/<subject>/start/<start_date>/end/<end_date>")
    print("\nMeeting Tools:")
    print("  GET  /api/meetings/id/<meeting_id>")
    print("  GET  /api/meetings/title/<title>")
    print("  GET  /api/meetings/attendance/<meeting_id>")
    print("  GET  /api/meetings/audience/<meeting_id>")
    print("  GET  /api/meetings/transcript/<meeting_id>")
    print("\nOneDrive Tools:")
    print("  GET  /api/onedrive/files")
    print("  GET  /api/onedrive/shared")
    print("  GET  /api/onedrive/file/<file_name>")
    print("\n  GET  /api/health")
    print("\nServer will start on http://localhost:5000")
    print("Web interface available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
