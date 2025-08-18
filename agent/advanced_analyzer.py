import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class AdvancedAnalyzer:
    
    @staticmethod
    def analyze_email_content(emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not emails:
            return {"error": "No emails to analyze"}
        
        analysis = {
            "content_insights": {},
            "communication_patterns": {},
            "priority_analysis": {},
            "relationship_insights": {},
            "timeline_analysis": {},
            "natural_summary": ""
        }
        
                          
        # Prefer full body content when available, fallback to bodyPreview
        all_content = " ".join([
            (email.get("subject", "") + " " + (email.get("body", "") or email.get("bodyPreview", "")))
            for email in emails
        ]).lower()
        
                            
        themes = AdvancedAnalyzer._extract_themes(all_content)
        analysis["content_insights"]["themes"] = themes
        
                                
        senders = [email.get("from", "Unknown") for email in emails]
        sender_freq = Counter(senders)
        analysis["communication_patterns"]["top_senders"] = sender_freq.most_common(5)
        
                           
        urgent_count = len([e for e in emails if any(
            keyword in e.get("subject", "").lower() or keyword in (e.get("body", "") or e.get("bodyPreview", "")).lower()
            for keyword in ["urgent", "asap", "critical", "emergency"]
        )])
        analysis["priority_analysis"]["urgent_emails"] = urgent_count
        
                           
        dates = []
        for email in emails:
            date_str = email.get("receivedDateTime", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(date_obj)
                except:
                    pass
        
        if dates:
            analysis["timeline_analysis"]["date_range"] = {
                "earliest": min(dates).strftime("%Y-%m-%d"),
                "latest": max(dates).strftime("%Y-%m-%d"),
                "total_days": (max(dates) - min(dates)).days + 1
            }
        
                                           
        analysis["natural_summary"] = AdvancedAnalyzer._generate_email_summary(analysis)
        
        return analysis
    
    @staticmethod
    def analyze_meeting_patterns(meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not meetings:
            return {"error": "No meetings to analyze"}
        
        analysis = {
            "schedule_insights": {},
            "participant_analysis": {},
            "meeting_efficiency": {},
            "collaboration_patterns": {},
            "natural_summary": ""
        }
        
                           
        meeting_times = []
        durations = []
        for meeting in meetings:
            start_time = meeting.get("start", {}).get("dateTime", "")
            end_time = meeting.get("end", {}).get("dateTime", "")
            
            if start_time and end_time:
                try:
                    start_obj = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_obj = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    meeting_times.append(start_obj)
                    duration = (end_obj - start_obj).total_seconds() / 3600
                    durations.append(duration)
                except:
                    pass
        
        if meeting_times:
            analysis["schedule_insights"]["total_meetings"] = len(meeting_times)
            analysis["schedule_insights"]["avg_duration"] = sum(durations) / len(durations) if durations else 0
            analysis["schedule_insights"]["total_time"] = sum(durations)
        
                              
        all_attendees = []
        organizers = []
        for meeting in meetings:
            attendees = meeting.get("attendees", [])
            for attendee in attendees:
                email = attendee.get("emailAddress", {}).get("address", "Unknown")
                all_attendees.append(email)
            
            organizer = meeting.get("organizer", {}).get("emailAddress", {}).get("address", "Unknown")
            organizers.append(organizer)
        
        attendee_freq = Counter(all_attendees)
        organizer_freq = Counter(organizers)
        
        analysis["participant_analysis"]["top_attendees"] = attendee_freq.most_common(5)
        analysis["participant_analysis"]["top_organizers"] = organizer_freq.most_common(5)
        
                                           
        analysis["natural_summary"] = AdvancedAnalyzer._generate_meeting_summary(analysis)
        
        return analysis
    
    @staticmethod
    def analyze_file_usage(files: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not files:
            return {"error": "No files to analyze"}
        
        analysis = {
            "storage_insights": {},
            "file_patterns": {},
            "access_patterns": {},
            "collaboration_insights": {},
            "natural_summary": ""
        }
        
                          
        total_size = sum(file.get("size", 0) for file in files)
        file_types = [file.get("name", "").split(".")[-1].lower() for file in files if "." in file.get("name", "")]
        type_freq = Counter(file_types)
        
        analysis["storage_insights"]["total_size_mb"] = total_size / (1024 * 1024)
        analysis["storage_insights"]["file_count"] = len(files)
        analysis["storage_insights"]["avg_file_size"] = total_size / len(files) if files else 0
        analysis["file_patterns"]["type_distribution"] = type_freq.most_common(5)
        
                         
        recent_files = []
        for file in files:
            modified = file.get("lastModifiedDateTime", "")
            if modified:
                try:
                    mod_obj = datetime.fromisoformat(modified.replace('Z', '+00:00'))
                    if (datetime.now() - mod_obj).days <= 7:
                        recent_files.append(file)
                except:
                    pass
        
        analysis["access_patterns"]["recent_files"] = len(recent_files)
        analysis["access_patterns"]["recent_activity_ratio"] = len(recent_files) / len(files) if files else 0
        
                                           
        analysis["natural_summary"] = AdvancedAnalyzer._generate_file_summary(analysis)
        
        return analysis
    
    @staticmethod
    def _extract_themes(content: str) -> List[str]:
                             
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
        
        words = re.findall(r'\b\w{4,}\b', content.lower())
        filtered_words = [word for word in words if word not in stop_words]
        
        word_freq = Counter(filtered_words)
        return [word for word, count in word_freq.most_common(10)]
    
    @staticmethod
    def _generate_email_summary(analysis: Dict[str, Any]) -> str:
        summary_parts = []
        
        if "communication_patterns" in analysis:
            top_senders = analysis["communication_patterns"].get("top_senders", [])
            if top_senders:
                top_sender = top_senders[0]
                summary_parts.append(f"Your most frequent contact is {top_sender[0]} with {top_sender[1]} emails.")
        
        if "priority_analysis" in analysis:
            urgent_count = analysis["priority_analysis"].get("urgent_emails", 0)
            if urgent_count > 0:
                summary_parts.append(f"There are {urgent_count} urgent emails requiring immediate attention.")
        
        if "content_insights" in analysis:
            themes = analysis["content_insights"].get("themes", [])
            if themes:
                theme_list = ", ".join(themes[:3])
                summary_parts.append(f"Key topics discussed include: {theme_list}.")
        
        if "timeline_analysis" in analysis:
            date_range = analysis["timeline_analysis"].get("date_range", {})
            if date_range:
                days = date_range.get("total_days", 0)
                summary_parts.append(f"This covers a {days}-day period from {date_range.get('earliest', '')} to {date_range.get('latest', '')}.")
        
        return " ".join(summary_parts) if summary_parts else "Email analysis completed."
    
    @staticmethod
    def _generate_meeting_summary(analysis: Dict[str, Any]) -> str:
        summary_parts = []
        
        if "schedule_insights" in analysis:
            insights = analysis["schedule_insights"]
            total_meetings = insights.get("total_meetings", 0)
            avg_duration = insights.get("avg_duration", 0)
            total_time = insights.get("total_time", 0)
            
            if total_meetings > 0:
                summary_parts.append(f"You have {total_meetings} meetings scheduled.")
                if avg_duration > 0:
                    summary_parts.append(f"Average meeting duration is {avg_duration:.1f} hours.")
                if total_time > 0:
                    summary_parts.append(f"Total meeting time is {total_time:.1f} hours.")
        
        if "participant_analysis" in analysis:
            top_attendees = analysis["participant_analysis"].get("top_attendees", [])
            top_organizers = analysis["participant_analysis"].get("top_organizers", [])
            
            if top_attendees:
                top_attendee = top_attendees[0]
                summary_parts.append(f"Most frequent attendee is {top_attendee[0]} ({top_attendee[1]} meetings).")
            
            if top_organizers:
                top_organizer = top_organizers[0]
                summary_parts.append(f"Most active organizer is {top_organizer[0]} ({top_organizer[1]} meetings).")
        
        return " ".join(summary_parts) if summary_parts else "Meeting analysis completed."
    
    @staticmethod
    def _generate_file_summary(analysis: Dict[str, Any]) -> str:
        summary_parts = []
        
        if "storage_insights" in analysis:
            insights = analysis["storage_insights"]
            total_size = insights.get("total_size_mb", 0)
            file_count = insights.get("file_count", 0)
            avg_size = insights.get("avg_file_size", 0)
            
            if file_count > 0:
                summary_parts.append(f"You have {file_count} files totaling {total_size:.1f} MB.")
                if avg_size > 0:
                    summary_parts.append(f"Average file size is {avg_size / (1024*1024):.1f} MB.")
        
        if "file_patterns" in analysis:
            type_dist = analysis["file_patterns"].get("type_distribution", [])
            if type_dist:
                most_common = type_dist[0]
                summary_parts.append(f"Most common file type is .{most_common[0]} ({most_common[1]} files).")
        
        if "access_patterns" in analysis:
            recent_count = analysis["access_patterns"].get("recent_files", 0)
            if recent_count > 0:
                summary_parts.append(f"{recent_count} files were modified in the last 7 days.")
        
        return " ".join(summary_parts) if summary_parts else "File analysis completed."
