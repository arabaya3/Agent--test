import os
import json
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

                            
load_dotenv()

try:
    import aixplain as ax
    HAS_AIXPLAIN = True
                                     
    api_key = os.getenv("AIXPLAIN_API_KEY") or os.getenv("TEAM_API_KEY")
    if api_key:
                                      
        os.environ["TEAM_API_KEY"] = api_key
except Exception as e:
    print(f"Warning: AIXplain not available: {e}")
    HAS_AIXPLAIN = False

from shared.auth import get_access_token
from email_tools.shared_email_ids import fetch_last_email_ids, get_cached_email_ids
from email_tools.by_id import retrieve_emails_by_ids
from email_tools.by_sender_date import retrieve_emails_by_sender_date
from email_tools.by_date_range import retrieve_emails_by_date_range
from email_tools.by_subject_date_range import retrieve_emails_by_subject_date_range
from calendar_tools.by_date import retrieve_meetings_by_date
from calendar_tools.by_organizer_date import retrieve_meetings_by_organizer_date
from calendar_tools.by_date_range import retrieve_meetings_by_date_range
from calendar_tools.by_subject_date_range import retrieve_meetings_by_subject_date_range
from meeting_tools.by_id import retrieve_meeting_by_id
from meeting_tools.by_title import retrieve_meetings_by_title
from meeting_tools.transcript import retrieve_transcript_by_meeting_id
from meeting_tools.audience import retrieve_meeting_audience
from meeting_tools.attendance import retrieve_attendance_by_meeting_id
from onedrive_tools.list_files import list_onedrive_files
from onedrive_tools.retrieve_files import retrieve_onedrive_file
from onedrive_tools.upload_files import upload_onedrive_file
from agent.advanced_analyzer import AdvancedAnalyzer


class NameResolver:
    
    def __init__(self):
        self.name_to_email_cache = {}
        self.email_to_name_cache = {}
    
    def extract_names_from_query(self, query: str) -> List[str]:
                              
        name_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',              
            r'\b[A-Z][a-z]+\b',               
            r'from ([A-Z][a-z]+)',               
            r'by ([A-Z][a-z]+)',              
            r'with ([A-Z][a-z]+)',               
            r'from ([A-Z]+ [A-Z][a-z]+)',                       
            r'from ([A-Z]+)',                
        ]
        
        names = []
        for pattern in name_patterns:
            matches = re.findall(pattern, query)
            names.extend(matches)
        
                                            
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'last', 'this', 'that', 'these', 'those'}
        names = [name for name in names if name.lower() not in common_words]
        
                                                  
        processed_names = []
        for name in names:
                                                      
            if ' ' in name:
                processed_names.append(name)
                                                                        
            else:
                                                                             
                full_name_pattern = rf'\b{name}\s+[A-Z][a-z]+\b'
                if re.search(full_name_pattern, query):
                                           
                    full_match = re.search(full_name_pattern, query)
                    if full_match:
                        processed_names.append(full_match.group())
                else:
                    processed_names.append(name)
        
        return list(set(processed_names))
    
    def resolve_name_to_email(self, name: str, user_id: str = None) -> Optional[str]:
                           
        if name in self.name_to_email_cache:
            return self.name_to_email_cache[name]
        
                                          
                                                                         
                                                      
        
                                                                        
        name_mappings = {
            'john': 'john.doe@example.com',
            'jane': 'jane.smith@example.com',
            'mike': 'mike.johnson@example.com',
            'sarah': 'sarah.wilson@example.com',
            'david': 'david.brown@example.com',
            'emma': 'emma.davis@example.com',
            'alex': 'alex.taylor@example.com',
            'lisa': 'lisa.anderson@example.com',
            'abdel': 'abdel.rahman@example.com',
            'abdel rahman': 'abdel.rahman@example.com',
            'rahman': 'abdel.rahman@example.com',
            'ABDEL': 'abdel.rahman@example.com',
            'ABDEL Rahman': 'abdel.rahman@example.com',
            'ABDEL rahman': 'abdel.rahman@example.com',
        }
        
                                               
        email = name_mappings.get(name) or name_mappings.get(name.lower())
        if email:
            self.name_to_email_cache[name] = email
            self.email_to_name_cache[email] = name
        
        return email
    
    def resolve_email_to_name(self, email: str) -> Optional[str]:
                           
        if email in self.email_to_name_cache:
            return self.email_to_name_cache[email]
        
                                 
        if '@' in email:
            username = email.split('@')[0]
                                               
            name = username.replace('.', ' ').replace('_', ' ').title()
            self.email_to_name_cache[email] = name
            self.name_to_email_cache[name] = email
            return name
        
        return None
    
    def smart_name_extraction(self, query: str) -> Dict[str, str]:
        names = self.extract_names_from_query(query)
        resolved = {}
        
        for name in names:
            email = self.resolve_name_to_email(name)
            if email:
                resolved[name] = email
        
        return resolved


class RealTimeProcessor:
    
    @staticmethod
    def get_current_time() -> datetime:
        return datetime.now()
    
    @staticmethod
    def parse_relative_dates(query: str) -> List[str]:
        current_date = datetime.now()
        dates = []
        
        query_lower = query.lower()
        
               
        if "today" in query_lower:
            dates.append(current_date.strftime("%Y-%m-%d"))
        
                   
        if "yesterday" in query_lower:
            yesterday = current_date - timedelta(days=1)
            dates.append(yesterday.strftime("%Y-%m-%d"))
        
                  
        if "tomorrow" in query_lower:
            tomorrow = current_date + timedelta(days=1)
            dates.append(tomorrow.strftime("%Y-%m-%d"))
        
                                            
        if "last email" in query_lower or "last emails" in query_lower:
                                                                                      
                                                                   
            start_date = current_date - timedelta(days=30)
            dates.extend([start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")])
        
                       
        if "recent" in query_lower and ("email" in query_lower or "emails" in query_lower):
                                                
            start_date = current_date - timedelta(days=7)
            dates.extend([start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")])
        
                   
        if "last week" in query_lower:
            end_date = current_date - timedelta(days=current_date.weekday() + 1)
            start_date = end_date - timedelta(days=7)
            dates.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
        
                   
        if "this week" in query_lower:
            start_date = current_date - timedelta(days=current_date.weekday())
            dates.extend([start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")])
        
                   
        if "next week" in query_lower:
            start_date = current_date + timedelta(days=7-current_date.weekday())
            end_date = start_date + timedelta(days=6)
            dates.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
        
                    
        if "last month" in query_lower:
            if current_date.month == 1:
                last_month = current_date.replace(year=current_date.year-1, month=12)
            else:
                last_month = current_date.replace(month=current_date.month-1)
            start_date = last_month.replace(day=1)
            end_date = current_date.replace(day=1) - timedelta(days=1)
            dates.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
        
                    
        if "this month" in query_lower:
            start_date = current_date.replace(day=1)
            dates.extend([start_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d")])
        
                    
        if "next month" in query_lower:
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year+1, month=1)
            else:
                next_month = current_date.replace(month=current_date.month+1)
            start_date = next_month.replace(day=1)
            if next_month.month == 12:
                end_date = next_month.replace(year=next_month.year+1, month=1) - timedelta(days=1)
            else:
                end_date = next_month.replace(month=next_month.month+1) - timedelta(days=1)
            dates.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
        
        return dates
    
    @staticmethod
    def get_context_info() -> Dict[str, Any]:
        now = datetime.now()
        return {
            "current_date": now.strftime("%Y-%m-%d"),
            "current_time": now.strftime("%H:%M:%S"),
            "current_weekday": now.strftime("%A"),
            "current_month": now.strftime("%B"),
            "current_year": now.year,
            "is_weekend": now.weekday() >= 5,
            "is_business_hours": 9 <= now.hour <= 17
        }


class ChatBot:
    
    def __init__(self):
        self.api_key = os.getenv("AIXPLAIN_API_KEY") or os.getenv("TEAM_API_KEY")
        self.model_id = os.getenv("AIXPLAIN_MODEL_ID")
        self.conversation_history = []
        self.context_memory = {
            "last_query_type": None,
            "last_data": None,
            "last_analysis": None,
            "current_user": None,
            "session_start": datetime.now().isoformat()
        }
        
    def _get_chat_prompt(self, user_message: str, context: Dict[str, Any]) -> str:
        context_info = RealTimeProcessor.get_context_info()
        
                                                
        recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        history_text = ""
        if recent_history:
            history_text = "\nRecent Conversation:\n"
            for entry in recent_history:
                history_text += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
        
                            
        memory_text = ""
        if self.context_memory["last_query_type"]:
            memory_text = f"\nContext Memory:\n- Last query type: {self.context_memory['last_query_type']}\n"
            if self.context_memory["last_analysis"]:
                memory_text += f"- Last analysis: {self.context_memory['last_analysis'][:200]}...\n"
        
        prompt = f"""You are an intelligent executive assistant with access to emails, meetings, calendar, and files. 

Current Context:
- Date: {context_info['current_date']}
- Time: {context_info['current_time']}
- Day: {context_info['current_weekday']}
- Business Hours: {'Yes' if context_info['is_business_hours'] else 'No'}

You can help with:
1. Email analysis and retrieval
2. Meeting scheduling and analysis
3. File management and OneDrive operations
4. General conversation and assistance
5. Data insights and reporting
6. Follow-up questions and clarifications

{history_text}{memory_text}

User Query: {user_message}

Please provide a helpful, conversational response. Consider the conversation history and context when responding. If the user is asking follow-up questions, reference previous information appropriately. If they're asking about data (emails, meetings, files), let them know you can help retrieve and analyze that information. If it's general conversation, be friendly and helpful.

Response:"""
        
        return prompt
    
    def chat(self, user_message: str, context: Dict[str, Any] = None) -> str:
        if not HAS_AIXPLAIN or not self.api_key or not self.model_id:
            return self._fallback_chat(user_message)
        
        try:
            prompt = self._get_chat_prompt(user_message, context or {})
            
            client = ax.Aixplain(api_key=self.api_key)
            if hasattr(client, 'Model'):
                model = client.Model.get(id=self.model_id)
                if model:
                    result = model.run(data=prompt)
                    if hasattr(result, 'data'):
                        response = result.data
                    elif isinstance(result, dict):
                        response = result.get("data", "")
                    else:
                        response = str(result)
                    
                                           
                    response = response.strip()
                    if response.startswith("Response:"):
                        response = response[9:].strip()
                    
                                                 
                    self.conversation_history.append({
                        "user": user_message,
                        "assistant": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return response
            
            return self._fallback_chat(user_message)
            
        except Exception as e:
            print(f"[ChatBot] Error: {e}")
            return self._fallback_chat(user_message)
    
    def update_context_memory(self, query_type: str, data: Any = None, analysis: str = None):
        self.context_memory["last_query_type"] = query_type
        self.context_memory["last_data"] = data
        self.context_memory["last_analysis"] = analysis
    
    def get_context_memory(self) -> Dict[str, Any]:
        return self.context_memory.copy()
    
    def _fallback_chat(self, user_message: str) -> str:
        message_lower = user_message.lower()
        
                   
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                return "Good morning! I'm your AI executive assistant. How can I help you today?"
            elif 12 <= current_hour < 17:
                return "Good afternoon! I'm here to help with your emails, meetings, and files. What would you like to know?"
            else:
                return "Good evening! I'm your AI assistant. How can I assist you?"
        
              
        if any(word in message_lower for word in ["help", "what can you do", "capabilities", "features"]):
            return (
                "I'm your AI executive assistant. I can help with:\n\n"
                "Emails: Retrieve and analyze your emails\n"
                "Meetings: Check calendar, analyze patterns, get transcripts\n"
                "Files: List, search, and analyze your OneDrive files\n"
                "Analysis: Insights about your communication patterns and data\n\n"
                "Examples:\n"
                "- Who sent the most emails last week?\n"
                "- What meetings do I have today?\n"
                "- Show me recent files\n"
                "- Analyze my email patterns"
            )
        
                   
        if any(word in message_lower for word in ["time", "date", "today", "current"]):
            context = RealTimeProcessor.get_context_info()
            return f"Today is {context['current_weekday']}, {context['current_month']} {context['current_date']}. The current time is {context['current_time']}."
        
                               
        if "weather" in message_lower:
            return "I don't have access to weather information, but I can help you with your emails, meetings, and files!"
        
                          
        return "I'm here to help with your emails, meetings, and files! You can ask me to retrieve data, analyze patterns, or just chat. What would you like to do?"


class EnhancedSmartAgent:
    
    def __init__(self):
        self.qa = QuestionAnswerer()
        self.analyzer = DataAnalyzer()
        self.advanced_analyzer = AdvancedAnalyzer()
        self.chatbot = ChatBot()
        self.real_time = RealTimeProcessor()
        self.name_resolver = NameResolver()
    
    def _run_aixplain_model(self, query: str) -> Optional[Dict[str, Any]]:
        if not HAS_AIXPLAIN:
            return None
        
        try:
            model_id = os.getenv("AIXPLAIN_MODEL_ID")
            if not model_id:
                return None
            
                                                             
            context_info = self.real_time.get_context_info()
            
            system_prompt = f"""
You are an intelligent enterprise assistant that can both retrieve data and answer questions about it.

Current Context:
- Date: {context_info['current_date']}
- Time: {context_info['current_time']}
- Day: {context_info['current_weekday']}

Available tools:
1. email_by_id - Retrieve emails by specific IDs
2. email_by_sender_date - Retrieve emails from a specific sender on a specific date
3. email_by_date_range - Retrieve emails within a date range
4. email_by_subject_date_range - Retrieve emails with specific subject within a date range
5. calendar_by_date - Get meetings on a specific date
6. calendar_by_organizer_date - Get meetings organized by someone on a specific date
7. calendar_by_date_range - Get meetings within a date range
8. calendar_by_subject_date_range - Get meetings with specific subject within a date range
9. meeting_by_id - Get meeting details by ID
10. meeting_by_title - Get meetings by title
11. meeting_transcript - Get meeting transcript by meeting ID
12. meeting_audience - Get meeting attendees by meeting ID
13. meeting_attendance - Get meeting attendance reports by meeting ID
14. onedrive_list - List files in OneDrive folder
15. onedrive_download - Download a file from OneDrive
16. onedrive_upload - Upload a file to OneDrive
17. chat - General conversation (not data-related)

Question types:
- Data retrieval: "emails from john@example.com on 2025-08-10"
- Analysis questions: "who sent the most emails", "how many urgent emails are there"
- Combined: "get emails from last week and tell me who sent the most"
- Summarization: "summarize emails from yesterday", "give me a summary of meetings"
- Chat: "hello", "how are you", "what's the weather"

IMPORTANT RULES:
- For data retrieval, require specific dates or use relative dates (today, yesterday, last week)
- For analysis questions, use the most recent data available
- For combined queries, first retrieve data then analyze it
- For summarization queries, use email_by_date_range or calendar_by_date_range to get data first
- For chat queries, use the chat tool
- For name-based queries like "emails from John", use email_by_date_range with a recent date range
- NEVER use email_by_sender_date_range (this tool doesn't exist)

Analyze the user query and return a JSON response with:
- tool: the appropriate tool name
- question_type: "retrieval", "analysis", "combined", or "chat"
- analysis_question: the specific question to answer (if applicable)
- Any required parameters

Examples:
Query: "emails from john@example.com today"
Response: {{"tool": "email_by_sender_date", "question_type": "retrieval", "sender": "john@example.com", "date": "{context_info['current_date']}"}}

Query: "emails from John"
Response: {{"tool": "email_by_date_range", "question_type": "retrieval", "start_date": "2025-08-11", "end_date": "{context_info['current_date']}"}}

Query: "who sent the most emails last week"
Response: {{"tool": "email_by_date_range", "question_type": "combined", "analysis_question": "who sent the most emails", "start_date": "2025-08-04", "end_date": "2025-08-10"}}

Query: "summarize emails from yesterday"
Response: {{"tool": "email_by_date_range", "question_type": "retrieval", "start_date": "2025-08-17", "end_date": "2025-08-17"}}

Query: "hello"
Response: {{"tool": "chat", "question_type": "chat"}}

Return only valid JSON, no additional text.
"""
            
            prompt = f"System: {system_prompt}\n\nUser: {query}\n\nAssistant:"
            
            client = ax.Aixplain(api_key=api_key)
            if hasattr(client, 'Model'):
                model = client.Model.get(id=model_id)
                if model:
                    result = model.run(data=prompt)
                    if hasattr(result, 'data'):
                        output = result.data
                    elif isinstance(result, dict):
                        output = result.get("data", "")
                    else:
                        output = str(result)
                    
                    try:
                        decision = json.loads(output)
                        return decision
                    except json.JSONDecodeError:
                        return None
        except Exception as e:
            print(f"[AIXplain] Error: {e}")
            return None
    
    def _parse_dates(self, query: str) -> List[str]:
                                  
        explicit_dates = re.findall(r"\d{4}-\d{2}-\d{2}", query)
        
                                 
        relative_dates = self.real_time.parse_relative_dates(query)
        
                                         
        all_dates = explicit_dates + relative_dates
        return list(dict.fromkeys(all_dates))                                            
    
    def _decide_with_rules(self, query: str) -> Dict[str, Any]:
        q = query.lower()
        emails = re.findall(r"[\w\.-]+@[\w\.-]+", query)
        dates = self._parse_dates(query)
        ids = re.findall(r"[A-Za-z0-9-]{10,}", query)
        quoted = re.findall(r"['\"]([^'\"]+)['\"]", query)
        
                                     
        follow_up_keywords = ["what about", "and", "also", "too", "as well", "in addition", "furthermore", "moreover", "besides", "additionally"]
        is_follow_up = any(keyword in q for keyword in follow_up_keywords)
        
                                                             
        chat_keywords = ["hello", "hi", "hey", "how are you", "good morning", "good afternoon", "good evening", "thanks", "thank you", "bye", "goodbye"]
        is_chat = any(keyword in q for keyword in chat_keywords) and not is_follow_up
        
        if is_chat:
            return {
                "tool": "chat",
                "question_type": "chat",
                "analysis_question": None,
                "is_follow_up": is_follow_up
            }
        
                                               
        analysis_keywords = ["how many", "who sent", "urgent", "follow up", "most", "least", "average", "summary", "analyze", "what are"]
        is_analysis = any(keyword in q for keyword in analysis_keywords)
        
                                 
        if is_analysis and dates:
            question_type = "combined"
        elif is_analysis:
            question_type = "analysis"
        else:
            question_type = "retrieval"
        
                                   
        analysis_question = None
        if is_analysis:
            analysis_question = query
        
                                   
        names = self.name_resolver.extract_names_from_query(query)
        resolved_names = self.name_resolver.smart_name_extraction(query)
        
                          
        if "email" in q or "emails" in q or "inbox" in q or (is_follow_up and names):
            
            if "id" in q and ids:
                return {
                    "tool": "email_by_id",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "email_ids": ids,
                    "is_follow_up": is_follow_up
                }
            
                                                                    
            if ("from" in q and (emails or names)) or (is_follow_up and names):
                sender = None
                resolved_name = None
                if emails:
                    sender = emails[1] if len(emails) > 1 else emails[0]
                elif names and resolved_names:
                                                 
                    first_name = list(resolved_names.keys())[0]
                    sender = resolved_names[first_name]
                    resolved_name = first_name
                
                if sender and dates and len(dates) == 1:
                    return {
                        "tool": "email_by_sender_date",
                        "question_type": question_type,
                        "analysis_question": analysis_question,
                        "sender": sender,
                        "date": dates[0],
                        "is_follow_up": is_follow_up,
                        "resolved_name": resolved_name
                    }
                elif sender:
                                                          
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=7)
                    return {
                        "tool": "email_by_date_range",
                        "question_type": question_type,
                        "analysis_question": analysis_question,
                        "sender": sender,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "is_follow_up": is_follow_up,
                        "resolved_name": resolved_name
                    }
            
                                       
            if len(dates) >= 2:
                return {
                    "tool": "email_by_date_range",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "start_date": dates[0],
                    "end_date": dates[1],
                    "is_follow_up": is_follow_up
                }
            
                                        
            if dates:
                return {
                    "tool": "email_by_date_range",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "start_date": dates[0],
                    "end_date": dates[0],
                    "is_follow_up": is_follow_up
                }
            
                                                         
            if is_analysis:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)
                return {
                    "tool": "email_by_date_range",
                    "question_type": "combined",
                    "analysis_question": analysis_question,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "is_follow_up": is_follow_up
                }
        
                            
        if "meeting" in q or "calendar" in q:
            if "transcript" in q:
                return {
                    "tool": "meeting_transcript",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "meeting_id": ids[0] if ids else None
                }
            if "attendees" in q or "audience" in q:
                return {
                    "tool": "meeting_audience",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "meeting_id": ids[0] if ids else None
                }
            if len(dates) >= 2:
                return {
                    "tool": "calendar_by_date_range",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "start_date": dates[0],
                    "end_date": dates[1]
                }
            if dates:
                return {
                    "tool": "calendar_by_date",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "date": dates[0]
                }
                                                         
            if is_analysis:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                return {
                    "tool": "calendar_by_date_range",
                    "question_type": "combined",
                    "analysis_question": analysis_question,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
        
                         
        if "file" in q or "onedrive" in q:
            if is_analysis:
                return {
                    "tool": "onedrive_list",
                    "question_type": "combined",
                    "analysis_question": analysis_question,
                    "folder_path": None,
                    "top": 100
                }
            else:
                return {
                    "tool": "onedrive_list",
                    "question_type": question_type,
                    "analysis_question": analysis_question,
                    "folder_path": quoted[0] if quoted else None,
                    "top": 50
                }
        
                                                        
        return {
            "tool": "chat",
            "question_type": "chat",
            "analysis_question": None
        }
    
    def handle_query(self, query: str, default_user_id: Optional[str] = None) -> Dict[str, Any]:
        print(f"[EnhancedSmartAgent] Processing query: {query}")
        
                                                  
        follow_up_keywords = ["what about", "and", "also", "too", "as well", "in addition", "furthermore", "moreover", "besides", "additionally"]
        is_follow_up_query = any(keyword in query.lower() for keyword in follow_up_keywords)
        
                                                                         
        names = self.name_resolver.extract_names_from_query(query)
        resolved_names = self.name_resolver.smart_name_extraction(query)
        
                                                                                   
        if is_follow_up_query:
            print("[EnhancedSmartAgent] Follow-up query detected, using rule-based logic")
            decision = self._decide_with_rules(query)
                                                                                      
        elif names and resolved_names:
            print("[EnhancedSmartAgent] Name-based query detected, using rule-based logic")
            decision = self._decide_with_rules(query)
        else:
                                                        
            decision = self._run_aixplain_model(query)
            
                                                             
            if not decision:
                print("[EnhancedSmartAgent] Using fallback rule-based logic")
                decision = self._decide_with_rules(query)
        
        tool = decision.get("tool")
        question_type = decision.get("question_type", "retrieval")
        analysis_question = decision.get("analysis_question")
        is_follow_up = decision.get("is_follow_up", False)
        resolved_name = decision.get("resolved_name")
        user_id = decision.get("user_id") or default_user_id
        
        print(f"[EnhancedSmartAgent] Selected tool: {tool}")
        print(f"[EnhancedSmartAgent] Question type: {question_type}")
        print(f"[EnhancedSmartAgent] Analysis question: {analysis_question}")
        print(f"[EnhancedSmartAgent] Is follow-up: {is_follow_up}")
        if resolved_name:
            print(f"[EnhancedSmartAgent] Resolved name: {resolved_name}")
        
                             
        if tool == "chat":
            chat_response = self.chatbot.chat(query)
            return {
                "tool": "chat",
                "question_type": "chat",
                "response": chat_response,
                "timestamp": datetime.now().isoformat(),
                "is_follow_up": is_follow_up
            }
        
                            
        if tool == "error":
            error_message = decision.get("message", "An error occurred")
            return {"tool": tool, "error": error_message, "answer": error_message}
        
                                               
        headers = None
        if tool and tool.startswith("email_"):
            token = get_access_token()
            if not token:
                raise RuntimeError("Failed to acquire access token")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            fetch_last_email_ids(headers, limit=100, user_id=user_id)
        
                                       
        data = None
        
                                                 
        if tool == "email_by_sender_date_range":
                                                                       
            print("[EnhancedSmartAgent] Invalid tool 'email_by_sender_date_range' detected, using fallback")
            tool = "email_by_date_range"
                                                          
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            decision["start_date"] = start_date.strftime("%Y-%m-%d")
            decision["end_date"] = end_date.strftime("%Y-%m-%d")
        
        if tool == "email_by_id":
            email_ids = decision.get("email_ids") or []
            data = retrieve_emails_by_ids(email_ids, headers, user_id)
        elif tool == "email_by_sender_date":
            sender = decision.get("sender")
            date = decision.get("date")
            data = retrieve_emails_by_sender_date(sender, date, headers, user_id)
            
                                                               
            if data and resolved_name:
                sender_name = self.name_resolver.resolve_email_to_name(sender)
                self.chatbot.update_context_memory(
                    "email_sender",
                    data,
                    f"Retrieved emails from {resolved_name} ({sender}) on {date}"
                )
        elif tool == "email_by_date_range":
            start_date = decision.get("start_date")
            end_date = decision.get("end_date")
            sender = decision.get("sender")                          
            
            if sender:
                                               
                all_data = retrieve_emails_by_date_range(start_date, end_date, headers, get_cached_email_ids(limit=100), user_id)
                data = [email for email in all_data if email.get("from") == sender]
            else:
                data = retrieve_emails_by_date_range(start_date, end_date, headers, get_cached_email_ids(limit=100), user_id)
            
                                                               
            if data:
                date_range = f"{start_date} to {end_date}"
                if resolved_name:
                    self.chatbot.update_context_memory(
                        "email_sender_range",
                        data,
                        f"Retrieved emails from {resolved_name} between {date_range}"
                    )
                else:
                    self.chatbot.update_context_memory(
                        "email_range",
                        data,
                        f"Retrieved emails between {date_range}"
                    )
        elif tool == "email_by_subject_date_range":
            data = retrieve_emails_by_subject_date_range(decision.get("subject"), decision.get("start_date"), decision.get("end_date"), headers, get_cached_email_ids(limit=100), user_id)
        elif tool == "calendar_by_date":
            data = retrieve_meetings_by_date(decision.get("date"), user_id)
        elif tool == "calendar_by_organizer_date":
            data = retrieve_meetings_by_organizer_date(decision.get("organizer"), decision.get("date"), user_id)
        elif tool == "calendar_by_date_range":
            data = retrieve_meetings_by_date_range(decision.get("start_date"), decision.get("end_date"), user_id)
        elif tool == "calendar_by_subject_date_range":
            data = retrieve_meetings_by_subject_date_range(decision.get("subject"), decision.get("start_date"), decision.get("end_date"), user_id)
        elif tool == "meeting_by_id":
            data = retrieve_meeting_by_id(decision.get("meeting_id"), user_id)
        elif tool == "meeting_by_title":
            data = retrieve_meetings_by_title(decision.get("title"), user_id)
        elif tool == "meeting_transcript":
            data = retrieve_transcript_by_meeting_id(decision.get("meeting_id"), user_id)
        elif tool == "meeting_audience":
            data = retrieve_meeting_audience(decision.get("meeting_id"), user_id)
        elif tool == "meeting_attendance":
            data = retrieve_attendance_by_meeting_id(decision.get("meeting_id"), user_id)
        elif tool == "onedrive_list":
            data = list_onedrive_files(user_id=user_id, folder_path=decision.get("folder_path"), top=int(decision.get("top", 50)))
        elif tool == "onedrive_download":
            item_path = decision.get("item_path")
            local_path = decision.get("local_path") or (os.path.join(".", os.path.basename(item_path)) if item_path else None)
            if not item_path:
                raise ValueError("item_path is required to download")
            _, meta = retrieve_onedrive_file(item_path=item_path, user_id=user_id, download_to=local_path)
            data = {"savedTo": local_path, "contentType": meta.get("content_type")}
        elif tool == "onedrive_upload":
            local_path = decision.get("local_path")
            destination_path = decision.get("destination_path")
            if not local_path or not destination_path:
                raise ValueError("Upload requires local_path and destination_path")
            item = upload_onedrive_file(file_path=local_path, destination_path=destination_path, user_id=user_id)
            data = {"name": item.get("name"), "size": item.get("size")}
        
                           
        data_count = len(data) if isinstance(data, list) else 1 if data else 0
        
        response = {
            "tool": tool,
            "question_type": question_type,
            "data_count": data_count,
            "timestamp": datetime.now().isoformat(),
            "is_follow_up": is_follow_up
        }
        
                                                   
        if data_count == 0 and tool != "chat":
            if resolved_name:
                response["message"] = f"No emails found from {resolved_name} in the specified date range."
            elif tool.startswith("email_"):
                response["message"] = "No emails found matching your criteria."
            elif tool.startswith("meeting_"):
                response["message"] = "No meetings found matching your criteria."
            elif tool.startswith("onedrive_"):
                response["message"] = "No files found matching your criteria."
        
                                       
        if resolved_name:
            response["resolved_name"] = resolved_name
            response["sender_email"] = decision.get("sender")
        
                                                 
        if is_follow_up:
            context_memory = self.chatbot.get_context_memory()
            response["conversation_context"] = {
                "last_query_type": context_memory.get("last_query_type"),
                "last_analysis": context_memory.get("last_analysis")
            }
        
                                                 
        if question_type in ["analysis", "combined"] and analysis_question and data:
            if tool.startswith("email_"):
                answer = self.qa.answer_email_questions(data, analysis_question)
                                       
                advanced_analysis = self.advanced_analyzer.analyze_email_content(data)
                if "natural_summary" in advanced_analysis:
                    response["advanced_insights"] = advanced_analysis["natural_summary"]
                
                                                                   
                self.chatbot.update_context_memory(
                    "email_analysis",
                    data,
                    f"Analyzed emails: {answer}"
                )
            elif tool.startswith("calendar_") or tool.startswith("meeting_"):
                answer = self.qa.answer_meeting_questions(data, analysis_question)
                                       
                advanced_analysis = self.advanced_analyzer.analyze_meeting_patterns(data)
                if "natural_summary" in advanced_analysis:
                    response["advanced_insights"] = advanced_analysis["natural_summary"]
                
                                                                   
                self.chatbot.update_context_memory(
                    "meeting_analysis",
                    data,
                    f"Analyzed meetings: {answer}"
                )
            elif tool.startswith("onedrive_"):
                answer = self.qa.answer_file_questions(data, analysis_question)
                                       
                advanced_analysis = self.advanced_analyzer.analyze_file_usage(data)
                if "natural_summary" in advanced_analysis:
                    response["advanced_insights"] = advanced_analysis["natural_summary"]
                
                                                                   
                self.chatbot.update_context_memory(
                    "file_analysis",
                    data,
                    f"Analyzed files: {answer}"
                )
            else:
                answer = "I can analyze the data but don't have specific analysis for this type of data."
            
            response["answer"] = answer
            response["analysis_question"] = analysis_question
        
                                                                                           
        if question_type == "retrieval" and data:
                                                      
            max_items = 10
            items = []
            if tool.startswith("email_") and isinstance(data, list):
                for e in data[:max_items]:
                    items.append({
                        "from": e.get("from", "Unknown"),
                        "subject": e.get("subject", "No Subject"),
                        "receivedDateTime": e.get("receivedDateTime", "Unknown"),
                        "hasAttachments": e.get("hasAttachments", False)
                    })
                response["natural_response"] = self._generate_fallback_email_summary(data, query)
            elif (tool.startswith("calendar_") or tool.startswith("meeting_")) and isinstance(data, list):
                for m in data[:max_items]:
                    items.append({
                        "subject": m.get("subject", "No Subject"),
                        "organizer": m.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown"),
                        "start": m.get("start", {}).get("dateTime", "Unknown"),
                        "end": m.get("end", {}).get("dateTime", "Unknown"),
                        "attendees": len(m.get("attendees", []))
                    })
                response["natural_response"] = self._generate_fallback_meeting_summary(data, query)
            elif tool.startswith("onedrive_") and isinstance(data, list):
                for f in data[:max_items]:
                    items.append({
                        "name": f.get("name", "Unknown"),
                        "size": f.get("size", 0),
                        "lastModifiedDateTime": f.get("lastModifiedDateTime", "Unknown"),
                        "type": "Folder" if f.get("isFolder", False) else "File"
                    })
                response["natural_response"] = self._generate_fallback_file_summary(data, query)
            if items:
                response["items"] = items
        
        return response
    
    def _generate_email_summary(self, emails: List[Dict[str, Any]], original_query: str) -> str:
        if not emails:
            return "No emails found for the specified criteria."
        
        try:
                                            
            email_summaries = []
            for i, email in enumerate(emails[:10], 1):                            
                sender = email.get("from", "Unknown")
                subject = email.get("subject", "No Subject")
                date = email.get("receivedDateTime", "Unknown")
                has_attachments = email.get("hasAttachments", False)
                preview = email.get("bodyPreview", "")[:100] + "..." if email.get("bodyPreview") else "No preview"
                
                email_summaries.append(f"{i}. From: {sender}\n   Subject: {subject}\n   Date: {date}\n   Attachments: {'Yes' if has_attachments else 'No'}\n   Preview: {preview}")
            
                                        
            prompt = f"""You are an intelligent executive assistant. The user asked: "{original_query}"

Here are the emails that were found:

{chr(10).join(email_summaries)}

Please provide a natural, conversational summary of these emails. Include:
1. A friendly opening acknowledging the user's request
2. The total number of emails found
3. Key details about the most important emails (senders, subjects, dates)
4. Any patterns you notice (e.g., multiple emails from same sender, urgent topics)
5. A brief mention of attachments if any
6. A helpful closing

Make it conversational and natural, as if you're speaking to the user directly. Keep it concise but informative.

Response:"""
            
                                              
            if HAS_AIXPLAIN and self.chatbot.api_key and self.chatbot.model_id:
                client = ax.Aixplain(api_key=self.chatbot.api_key)
                if hasattr(client, 'Model'):
                    model = client.Model.get(id=self.chatbot.model_id)
                    if model:
                        result = model.run(data=prompt)
                        if hasattr(result, 'data'):
                            summary = result.data
                        elif isinstance(result, dict):
                            summary = result.get("data", "")
                        else:
                            summary = str(result)
                        
                                               
                        summary = summary.strip()
                        if summary.startswith("Response:"):
                            summary = summary[9:].strip()
                        
                        return summary
            
                                            
            return self._generate_fallback_email_summary(emails, original_query)
            
        except Exception as e:
            print(f"[EnhancedSmartAgent] Error generating email summary: {e}")
            return self._generate_fallback_email_summary(emails, original_query)
    
    def _generate_fallback_email_summary(self, emails: List[Dict[str, Any]], original_query: str) -> str:
        if not emails:
            return "No emails found for the specified criteria."
        
        total_emails = len(emails)
        senders = {}
        subjects = []
        attachments = 0
        
        for email in emails:
            sender = email.get("from", "Unknown")
            senders[sender] = senders.get(sender, 0) + 1
            
            subject = email.get("subject", "No Subject")
            if subject not in subjects:
                subjects.append(subject)
            
            if email.get("hasAttachments", False):
                attachments += 1
        
        top_sender = max(senders.items(), key=lambda x: x[1])[0] if senders else "Unknown"
        
        summary = f"Here are the emails you received yesterday:\n\n"
        summary += f"I found {total_emails} email(s) for you. "
        
        if total_emails == 1:
            email = emails[0]
            summary += f"The email is from {email.get('from', 'Unknown')} with subject '{email.get('subject', 'No Subject')}' "
            summary += f"received on {email.get('receivedDateTime', 'Unknown')}. "
            if email.get('hasAttachments', False):
                summary += "It has attachments. "
        else:
            summary += f"Most emails are from {top_sender} ({senders[top_sender]} emails). "
            if attachments > 0:
                summary += f"{attachments} email(s) have attachments. "
            summary += f"Key subjects include: {', '.join(subjects[:3])}"
            if len(subjects) > 3:
                summary += f" and {len(subjects) - 3} more."
        
        summary += "\n\nWould you like me to provide more details about any specific email?"
        
        return summary
    
    def _generate_meeting_summary(self, meetings: List[Dict[str, Any]], original_query: str) -> str:
        if not meetings:
            return "No meetings found for the specified criteria."
        
        try:
                                              
            meeting_summaries = []
            for i, meeting in enumerate(meetings[:10], 1):                              
                subject = meeting.get("subject", "No Subject")
                organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
                start = meeting.get("start", {}).get("dateTime", "Unknown")
                end = meeting.get("end", {}).get("dateTime", "Unknown")
                attendees_count = len(meeting.get("attendees", []))
                
                meeting_summaries.append(f"{i}. Subject: {subject}\n   Organizer: {organizer}\n   Start: {start}\n   End: {end}\n   Attendees: {attendees_count}")
            
                                        
            prompt = f"""You are an intelligent executive assistant. The user asked: "{original_query}"

Here are the meetings that were found:

{chr(10).join(meeting_summaries)}

Please provide a natural, conversational summary of these meetings. Include:
1. A friendly opening acknowledging the user's request
2. The total number of meetings found
3. Key details about the most important meetings (subjects, organizers, times)
4. Any patterns you notice (e.g., multiple meetings with same organizer, time conflicts)
5. A brief mention of attendee counts
6. A helpful closing

Make it conversational and natural, as if you're speaking to the user directly. Keep it concise but informative.

Response:"""
            
                                              
            if HAS_AIXPLAIN and self.chatbot.api_key and self.chatbot.model_id:
                client = ax.Aixplain(api_key=self.chatbot.api_key)
                if hasattr(client, 'Model'):
                    model = client.Model.get(id=self.chatbot.model_id)
                    if model:
                        result = model.run(data=prompt)
                        if hasattr(result, 'data'):
                            summary = result.data
                        elif isinstance(result, dict):
                            summary = result.get("data", "")
                        else:
                            summary = str(result)
                        
                                               
                        summary = summary.strip()
                        if summary.startswith("Response:"):
                            summary = summary[9:].strip()
                        
                        return summary
            
                                            
            return self._generate_fallback_meeting_summary(meetings, original_query)
            
        except Exception as e:
            print(f"[EnhancedSmartAgent] Error generating meeting summary: {e}")
            return self._generate_fallback_meeting_summary(meetings, original_query)
    
    def _generate_fallback_meeting_summary(self, meetings: List[Dict[str, Any]], original_query: str) -> str:
        if not meetings:
            return "No meetings found for the specified criteria."
        
        total_meetings = len(meetings)
        organizers = {}
        
        for meeting in meetings:
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            organizers[organizer] = organizers.get(organizer, 0) + 1
        
        top_organizer = max(organizers.items(), key=lambda x: x[1])[0] if organizers else "Unknown"
        
        summary = f"Here are your meetings:\n\n"
        summary += f"I found {total_meetings} meeting(s) for you. "
        
        if total_meetings == 1:
            meeting = meetings[0]
            summary += f"The meeting is '{meeting.get('subject', 'No Subject')}' organized by {meeting.get('organizer', {}).get('emailAddress', {}).get('address', 'Unknown')} "
            summary += f"from {meeting.get('start', {}).get('dateTime', 'Unknown')} to {meeting.get('end', {}).get('dateTime', 'Unknown')}. "
        else:
            summary += f"Most meetings are organized by {top_organizer} ({organizers[top_organizer]} meetings). "
        
        summary += "\n\nWould you like me to provide more details about any specific meeting?"
        
        return summary
    
    def _generate_file_summary(self, files: List[Dict[str, Any]], original_query: str) -> str:
        if not files:
            return "No files found for the specified criteria."
        
        try:
                                           
            file_summaries = []
            for i, file in enumerate(files[:10], 1):                           
                name = file.get("name", "Unknown")
                size = file.get("size", 0)
                size_mb = size / (1024 * 1024) if size > 0 else 0
                modified = file.get("lastModifiedDateTime", "Unknown")
                is_folder = file.get("isFolder", False)
                
                file_summaries.append(f"{i}. Name: {name}\n   Size: {size_mb:.2f} MB\n   Modified: {modified}\n   Type: {'Folder' if is_folder else 'File'}")
            
                                        
            prompt = f"""You are an intelligent executive assistant. The user asked: "{original_query}"

Here are the files that were found:

{chr(10).join(file_summaries)}

Please provide a natural, conversational summary of these files. Include:
1. A friendly opening acknowledging the user's request
2. The total number of files found
3. Key details about the most important files (names, sizes, types)
4. Any patterns you notice (e.g., file types, sizes, recent modifications)
5. A brief mention of total storage used
6. A helpful closing

Make it conversational and natural, as if you're speaking to the user directly. Keep it concise but informative.

Response:"""
            
                                              
            if HAS_AIXPLAIN and self.chatbot.api_key and self.chatbot.model_id:
                client = ax.Aixplain(api_key=self.chatbot.api_key)
                if hasattr(client, 'Model'):
                    model = client.Model.get(id=self.chatbot.model_id)
                    if model:
                        result = model.run(data=prompt)
                        if hasattr(result, 'data'):
                            summary = result.data
                        elif isinstance(result, dict):
                            summary = result.get("data", "")
                        else:
                            summary = str(result)
                        
                                               
                        summary = summary.strip()
                        if summary.startswith("Response:"):
                            summary = summary[9:].strip()
                        
                        return summary
            
                                            
            return self._generate_fallback_file_summary(files, original_query)
            
        except Exception as e:
            print(f"[EnhancedSmartAgent] Error generating file summary: {e}")
            return self._generate_fallback_file_summary(files, original_query)
    
    def _generate_fallback_file_summary(self, files: List[Dict[str, Any]], original_query: str) -> str:
        if not files:
            return "No files found for the specified criteria."
        
        total_files = len(files)
        total_size = sum(file.get("size", 0) for file in files)
        total_size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
        file_types = {}
        
        for file in files:
            if not file.get("isFolder", False):
                file_type = file.get("name", "").split(".")[-1] if "." in file.get("name", "") else "unknown"
                file_types[file_type] = file_types.get(file_type, 0) + 1
        
        summary = f"Here are your files:\n\n"
        summary += f"I found {total_files} file(s) for you. "
        summary += f"Total size: {total_size_mb:.2f} MB. "
        
        if file_types:
            top_type = max(file_types.items(), key=lambda x: x[1])[0]
            summary += f"Most common file type is {top_type} ({file_types[top_type]} files). "
        
        summary += "\n\nWould you like me to provide more details about any specific file?"
        
        return summary


                                                                       
class DataAnalyzer:
    
    @staticmethod
    def analyze_emails(emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not emails:
            return {"count": 0, "senders": {}, "subjects": [], "dates": [], "attachments": 0}
        
        senders = {}
        subjects = []
        dates = []
        attachments = 0
        
        for email in emails:
                           
            sender = email.get("from", "Unknown")
            senders[sender] = senders.get(sender, 0) + 1
            
                              
            subject = email.get("subject", "No Subject")
            if subject not in subjects:
                subjects.append(subject)
            
                           
            date = email.get("receivedDateTime", "Unknown")
            dates.append(date)
            
                               
            if email.get("hasAttachments", False):
                attachments += 1
        
        return {
            "count": len(emails),
            "senders": senders,
            "subjects": subjects,
            "dates": dates,
            "attachments": attachments,
            "top_sender": max(senders.items(), key=lambda x: x[1])[0] if senders else None
        }
    
    @staticmethod
    def analyze_meetings(meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not meetings:
            return {"count": 0, "organizers": {}, "attendees": [], "subjects": []}
        
        organizers = {}
        attendees = []
        subjects = []
        
        for meeting in meetings:
                              
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            organizers[organizer] = organizers.get(organizer, 0) + 1
            
                              
            subject = meeting.get("subject", "No Subject")
            if subject not in subjects:
                subjects.append(subject)
            
                               
            meeting_attendees = meeting.get("attendees", [])
            for attendee in meeting_attendees:
                attendee_email = attendee.get("emailAddress", {}).get("address", "Unknown")
                if attendee_email not in attendees:
                    attendees.append(attendee_email)
        
        return {
            "count": len(meetings),
            "organizers": organizers,
            "attendees": attendees,
            "subjects": subjects,
            "top_organizer": max(organizers.items(), key=lambda x: x[1])[0] if organizers else None
        }
    
    @staticmethod
    def analyze_files(files: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not files:
            return {"count": 0, "types": {}, "sizes": [], "total_size": 0}
        
        types = {}
        sizes = []
        total_size = 0
        
        for file in files:
                              
            file_type = file.get("name", "").split(".")[-1] if "." in file.get("name", "") else "unknown"
            types[file_type] = types.get(file_type, 0) + 1
            
                           
            size = file.get("size", 0)
            sizes.append(size)
            total_size += size
        
        return {
            "count": len(files),
            "types": types,
            "sizes": sizes,
            "total_size": total_size,
            "average_size": total_size / len(files) if files else 0,
            "top_type": max(types.items(), key=lambda x: x[1])[0] if types else None
        }


class QuestionAnswerer:
    
    @staticmethod
    def answer_email_questions(emails: List[Dict[str, Any]], question: str) -> str:
        analysis = DataAnalyzer.analyze_emails(emails)
        q = question.lower()
        
        if "how many" in q and "email" in q:
            return f"There are {analysis['count']} emails in the dataset."
        
        if "who sent" in q and "most" in q:
            if analysis['top_sender']:
                return f"The person who sent the most emails is {analysis['top_sender']} with {analysis['senders'][analysis['top_sender']]} emails."
            else:
                return "No emails found to analyze."
        
        if "attachment" in q:
            return f"There are {analysis['attachments']} emails with attachments."
        
        if "urgent" in q or "important" in q:
                                                                
            urgent_keywords = ["urgent", "important", "asap", "critical", "emergency", "deadline"]
            urgent_count = 0
            for email in emails:
                subject = email.get("subject", "").lower()
                if any(keyword in subject for keyword in urgent_keywords):
                    urgent_count += 1
            return f"There are {urgent_count} potentially urgent emails."
        
        return f"Found {analysis['count']} emails. Top sender is {analysis['top_sender']} with {analysis['senders'].get(analysis['top_sender'], 0)} emails."
    
    @staticmethod
    def answer_meeting_questions(meetings: List[Dict[str, Any]], question: str) -> str:
        analysis = DataAnalyzer.analyze_meetings(meetings)
        q = question.lower()
        
        if "how many" in q and "meeting" in q:
            return f"There are {analysis['count']} meetings in the dataset."
        
        if "who organized" in q and "most" in q:
            if analysis['top_organizer']:
                return f"The person who organized the most meetings is {analysis['top_organizer']} with {analysis['organizers'][analysis['top_organizer']]} meetings."
            else:
                return "No meetings found to analyze."
        
        if "attendee" in q:
            return f"There are {len(analysis['attendees'])} unique attendees across all meetings."
        
        return f"Found {analysis['count']} meetings. Top organizer is {analysis['top_organizer']} with {analysis['organizers'].get(analysis['top_organizer'], 0)} meetings."
    
    @staticmethod
    def answer_file_questions(files: List[Dict[str, Any]], question: str) -> str:
        analysis = DataAnalyzer.analyze_files(files)
        q = question.lower()
        
        if "how many" in q and "file" in q:
            return f"There are {analysis['count']} files in the dataset."
        
        if "type" in q and "most" in q:
            if analysis['top_type']:
                return f"The most common file type is {analysis['top_type']} with {analysis['types'][analysis['top_type']]} files."
            else:
                return "No files found to analyze."
        
        if "size" in q:
            total_mb = analysis['total_size'] / (1024 * 1024)
            avg_mb = analysis['average_size'] / (1024 * 1024)
            return f"Total size is {total_mb:.2f} MB. Average file size is {avg_mb:.2f} MB."
        
        return f"Found {analysis['count']} files. Total size is {analysis['total_size'] / (1024 * 1024):.2f} MB."


def test_enhanced_agent():
    agent = EnhancedSmartAgent()
    
                        
    test_queries = [
        "hello",
        "what time is it?",
        "emails from today",
        "meetings this week",
        "who sent the most emails last week",
        "how are you?",
        "files in Documents folder",
        "what can you do?",
        "emails from yesterday",
        "meetings next week"
    ]
    
                             
    name_queries = [
        "emails from John",
        "emails from Sarah today",
        "meetings with Mike this week",
        "who sent the most emails from Jane last week"
    ]
    
                                  
    follow_up_queries = [
        "emails from John",
        "what about Sarah?",
        "and Mike too",
        "also show me recent files"
    ]
    
                             
    last_email_queries = [
        "last email",
        "last emails from John",
        "recent emails",
        "emails from last week"
    ]
    
    all_queries = test_queries + name_queries + follow_up_queries + last_email_queries
    
    print("Testing Enhanced Smart Agent...")
    print("=" * 60)
    
    for i, query in enumerate(all_queries, 1):
        print(f"\nQuery {i}/{len(all_queries)}: {query}")
        print("-" * 40)
        try:
            result = agent.handle_query(query, "executive.assistant@menadevs.io")
            
                                     
            print(f"Tool: {result.get('tool', 'Unknown')}")
            print(f"Question Type: {result.get('question_type', 'Unknown')}")
            print(f"Data Count: {result.get('data_count', 0)}")
            print(f"Is Follow-up: {result.get('is_follow_up', False)}")
            
            if "resolved_name" in result:
                print(f"Resolved Name: {result['resolved_name']}")
                print(f"Sender Email: {result.get('sender_email', 'Unknown')}")
            
            if "conversation_context" in result:
                print(f"Conversation Context: {result['conversation_context']}")
            
            if "response" in result:
                print(f"Chat Response: {result['response']}")
            
            if "answer" in result:
                print(f"Answer: {result['answer']}")
            
            if "advanced_insights" in result:
                print(f"Advanced Insights: {result['advanced_insights']}")
            
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 40)


if __name__ == "__main__":
    test_enhanced_agent()
