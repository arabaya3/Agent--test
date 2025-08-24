from flask import Flask, request, jsonify, render_template
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the email tools
from Email_Tools.email_by_sender import search_emails_by_sender
from Email_Tools.email_by_id import search_email_by_id
from Email_Tools.email_by_subject import search_emails_by_subject

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint with web interface"""
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "message": "Email Tools API Server",
        "version": "1.0.0",
        "endpoints": {
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
        }
    })

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

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Email Tools API is running"
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
    
    print("Starting Email Tools API Server...")
    print("Available endpoints:")
    print("  GET  /                    - Web interface")
    print("  GET  /api/docs            - API documentation")
    print("  GET  /api/emails/sender/<sender>")
    print("  GET  /api/emails/id/<email_id>")
    print("  GET  /api/emails/subject/<subject>")
    print("  POST /api/emails/search")
    print("  GET  /api/health")
    print("\nServer will start on http://localhost:5000")
    print("Web interface available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
