import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the enhanced smart agent
from agent.enhanced_smart_agent import EnhancedSmartAgent

# Default user ID for application permissions
DEFAULT_USER_ID = os.getenv('DEFAULT_USER_ID', "executive.assistant@menadevs.io")

def print_banner():
    """Print the enhanced application banner."""
    print("=" * 80)
    print("🤖 AIXPLAIN ENHANCED SMART EXECUTIVE ASSISTANT")
    print("=" * 80)
    print("Real-time intelligent data retrieval, analysis, and conversational AI")
    print("=" * 80)

def print_help():
    """Print enhanced help information."""
    print("\n📋 AVAILABLE QUERY TYPES:")
    print("-" * 50)
    print("💬 CHAT QUERIES:")
    print("  • 'hello', 'hi', 'how are you'")
    print("  • 'what time is it?', 'what day is today?'")
    print("  • 'what can you do?', 'help'")
    print()
    print("📧 EMAIL QUERIES (with real-time dates & names):")
    print("  • 'emails from today'")
    print("  • 'emails from yesterday'")
    print("  • 'emails from last week'")
    print("  • 'emails from this month'")
    print("  • 'emails from John' (name-based)")
    print("  • 'emails from Sarah today' (name + date)")
    print("  • 'last email' (intelligent detection)")
    print("  • 'recent emails'")
    print("  • 'who sent the most emails last week'")
    print("  • 'how many urgent emails do I have'")
    print()
    print("🔄 FOLLOW-UP QUERIES:")
    print("  • 'what about Sarah?' (follow-up)")
    print("  • 'and Mike too' (additional)")
    print("  • 'also show me recent files' (combine)")
    print("  • 'emails from John' → 'what about Sarah?'")
    print()
    print("📅 MEETING QUERIES (with real-time dates):")
    print("  • 'meetings today'")
    print("  • 'meetings this week'")
    print("  • 'meetings with Mike' (name-based)")
    print("  • 'meetings next week'")
    print("  • 'meetings last month'")
    print("  • 'who organized the most meetings'")
    print("  • 'upcoming meetings'")
    print()
    print("📁 FILE QUERIES:")
    print("  • 'list files in Documents folder'")
    print("  • 'how many files are in my OneDrive'")
    print("  • 'recent files'")
    print("  • 'large files'")
    print()
    print("🔍 ANALYSIS QUERIES:")
    print("  • 'analyze my emails from last week'")
    print("  • 'summarize my meetings'")
    print("  • 'what are the main topics in my emails'")
    print("  • 'who are my most frequent contacts'")
    print("-" * 50)

def interactive_mode():
    """Run the enhanced assistant in interactive mode."""
    agent = EnhancedSmartAgent()
    user_id = DEFAULT_USER_ID
    
    print_banner()
    print_help()
    
    print(f"\n👤 Using user ID: {user_id}")
    print("💡 Type 'help' for query examples, 'quit' to exit")
    print("🕐 Real-time awareness: The assistant knows the current date and time")
    print("🤖 Chat mode: Say hello or ask general questions")
    print("👤 Name resolution: Use names instead of emails (e.g., 'emails from John')")
    print("🔄 Follow-up conversations: Ask follow-up questions naturally")
    print("📧 Smart last email: Intelligent detection of recent emails")
    print("=" * 80)
    
    while True:
        try:
            # Get user input
            query = input("\n🤖 Ask me anything: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'user':
                new_user = input(f"Enter new user ID (current: {user_id}): ").strip()
                if new_user:
                    user_id = new_user
                    print(f"✅ User ID changed to: {user_id}")
                continue
            
            if query.lower() == 'time':
                from agent.enhanced_smart_agent import RealTimeProcessor
                context = RealTimeProcessor.get_context_info()
                print(f"🕐 Current time: {context['current_time']}")
                print(f"📅 Current date: {context['current_date']}")
                print(f"📆 Day: {context['current_weekday']}")
                continue
            
            # Process the query
            print(f"\n🔄 Processing: {query}")
            print("-" * 60)
            
            start_time = datetime.now()
            result = agent.handle_query(query, user_id)
            end_time = datetime.now()
            
            # Display results
            print(f"\n✅ Query completed in {(end_time - start_time).total_seconds():.2f}s")
            print("=" * 60)
            
            # Show chat response if available
            if result.get("question_type") == "chat":
                print(f"\n💬 CHAT RESPONSE:")
                print(f"   {result.get('response', 'No response')}")
            
            # Show the answer if available
            if "answer" in result:
                print(f"\n💡 ANSWER:")
                print(f"   {result['answer']}")
            
            # Show natural language response if available
            if "natural_response" in result:
                print(f"\n💬 NATURAL RESPONSE:")
                print(f"   {result['natural_response']}")
            
            # Show advanced insights if available
            if "advanced_insights" in result:
                print(f"\n🔍 ADVANCED INSIGHTS:")
                print(f"   {result['advanced_insights']}")
            
            # Show summary
            if "summary" in result:
                print(f"\n📊 SUMMARY:")
                print(f"   {result['summary']}")
            else:
                print(f"\n📊 SUMMARY:")
                print(f"   Retrieved {result.get('data_count', 0)} item(s)")
            
            # Show helpful messages
            if "message" in result:
                print(f"\n💡 MESSAGE:")
                print(f"   {result['message']}")
            
            # Show context information
            if "context" in result:
                context = result["context"]
                print(f"\n🕐 CONTEXT:")
                print(f"   Date: {context.get('current_date', 'Unknown')}")
                print(f"   Time: {context.get('current_time', 'Unknown')}")
                print(f"   Day: {context.get('current_weekday', 'Unknown')}")
            
            # Show name resolution information
            if "resolved_name" in result:
                print(f"\n👤 NAME RESOLUTION:")
                print(f"   Name: {result['resolved_name']}")
                print(f"   Email: {result.get('sender_email', 'Unknown')}")
            
            # Show follow-up context
            if "conversation_context" in result:
                context = result["conversation_context"]
                print(f"\n🔄 FOLLOW-UP CONTEXT:")
                print(f"   Last query type: {context.get('last_query_type', 'Unknown')}")
                if context.get('last_analysis'):
                    print(f"   Last analysis: {context['last_analysis'][:100]}...")
            
            # Show detailed results
            print(f"\n🔧 TECHNICAL DETAILS:")
            print(f"   Tool used: {result.get('tool', 'Unknown')}")
            print(f"   Question type: {result.get('question_type', 'Unknown')}")
            print(f"   Data count: {result.get('data_count', 0)}")
            print(f"   Timestamp: {result.get('timestamp', 'Unknown')}")
            print(f"   Is follow-up: {result.get('is_follow_up', False)}")
            
            if "analysis_question" in result:
                print(f"   Analysis question: {result['analysis_question']}")
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            
            print("=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Try rephrasing your query or type 'help' for examples")

def batch_mode():
    """Run the enhanced assistant in batch mode for testing multiple queries."""
    agent = EnhancedSmartAgent()
    user_id = DEFAULT_USER_ID
    
    print_banner()
    print("🧪 ENHANCED BATCH TESTING MODE")
    print("=" * 80)
    
    # Enhanced test queries with real-time awareness, names, and follow-ups
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
        "meetings next week",
        "emails from last month",
        "analyze my meetings from this month",
        "recent files",
        "upcoming meetings",
        # Name-based queries
        "emails from John",
        "emails from Sarah today",
        "meetings with Mike this week",
        # Follow-up queries
        "what about Sarah?",
        "and Mike too",
        "also show me recent files",
        # Last email queries
        "last email",
        "last emails from John",
        "recent emails"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}/{len(test_queries)}: {query}")
        print("-" * 60)
        
        try:
            start_time = datetime.now()
            result = agent.handle_query(query, user_id)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Completed in {duration:.2f}s")
            print(f"📊 Tool: {result.get('tool', 'Unknown')}")
            print(f"📈 Question Type: {result.get('question_type', 'Unknown')}")
            
            # Show chat response
            if result.get("question_type") == "chat":
                print(f"💬 Chat Response: {result.get('response', 'No response')}")
            
            # Show answer
            if "answer" in result:
                print(f"💡 Answer: {result['answer']}")
            
            # Show advanced insights
            if "advanced_insights" in result:
                print(f"🔍 Advanced Insights: {result['advanced_insights']}")
            
            results.append({
                "query": query,
                "result": result,
                "duration": duration,
                "success": "error" not in result
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "query": query,
                "result": {"error": str(e)},
                "duration": 0,
                "success": False
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 ENHANCED BATCH TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r["success"])
    total_duration = sum(r["duration"] for r in results)
    
    print(f"✅ Successful queries: {successful}/{len(results)}")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print(f"📊 Average time per query: {total_duration/len(results):.2f}s")
    
    if successful > 0:
        avg_success_time = sum(r["duration"] for r in results if r["success"]) / successful
        print(f"📈 Average successful query time: {avg_success_time:.2f}s")
    
    # Categorize results
    chat_queries = [r for r in results if r["result"].get("question_type") == "chat"]
    data_queries = [r for r in results if r["result"].get("question_type") != "chat"]
    
    print(f"\n💬 Chat queries: {len(chat_queries)}")
    print(f"📊 Data queries: {len(data_queries)}")
    
    print("\n📋 DETAILED RESULTS:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        query_type = result["result"].get("question_type", "Unknown")
        print(f"   {i}. {status} [{query_type}] {result['query']} ({result['duration']:.2f}s)")

def demo_mode():
    """Run a demonstration of the enhanced capabilities."""
    agent = EnhancedSmartAgent()
    user_id = DEFAULT_USER_ID
    
    print_banner()
    print("🎭 ENHANCED CAPABILITIES DEMONSTRATION")
    print("=" * 80)
    
    # Real-time context demonstration
    from agent.enhanced_smart_agent import RealTimeProcessor
    context = RealTimeProcessor.get_context_info()
    
    print(f"\n🕐 REAL-TIME AWARENESS:")
    print(f"   Current Date: {context['current_date']}")
    print(f"   Current Time: {context['current_time']}")
    print(f"   Day of Week: {context['current_weekday']}")
    print(f"   Month: {context['current_month']}")
    print(f"   Year: {context['current_year']}")
    print(f"   Weekend: {'Yes' if context['is_weekend'] else 'No'}")
    print(f"   Business Hours: {'Yes' if context['is_business_hours'] else 'No'}")
    
    # Chat capabilities demonstration
    print(f"\n💬 CHAT CAPABILITIES:")
    chat_demos = [
        "hello",
        "what time is it?",
        "how are you?",
        "what can you do?"
    ]
    
    for demo_query in chat_demos:
        print(f"\n   User: {demo_query}")
        try:
            result = agent.handle_query(demo_query, user_id)
            response = result.get("response", "No response")
            print(f"   Assistant: {response}")
        except Exception as e:
            print(f"   Assistant: Error - {e}")
    
    # Real-time date processing demonstration
    print(f"\n📅 REAL-TIME DATE PROCESSING:")
    date_demos = [
        "emails from today",
        "meetings this week",
        "emails from yesterday",
        "meetings next week"
    ]
    
    for demo_query in date_demos:
        print(f"\n   Query: {demo_query}")
        try:
            result = agent.handle_query(demo_query, user_id)
            tool = result.get("tool", "Unknown")
            question_type = result.get("question_type", "Unknown")
            print(f"   Tool: {tool}")
            print(f"   Type: {question_type}")
            if "context" in result:
                print(f"   Context: {result['context']}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n🎉 DEMONSTRATION COMPLETE!")
    print("The enhanced assistant can now:")
    print("✅ Understand real-time context (current date/time)")
    print("✅ Process relative dates (today, yesterday, last week)")
    print("✅ Engage in natural conversation")
    print("✅ Provide intelligent data analysis")
    print("✅ Handle complex queries with context awareness")
    print("✅ Resolve names to email addresses")
    print("✅ Handle follow-up conversations")
    print("✅ Intelligently detect 'last email' queries")
    print("✅ Maintain conversation context and memory")

def main():
    """Main entry point for the enhanced assistant."""
    print_banner()
    
    print("\n🎯 SELECT MODE:")
    print("1. Interactive Mode (chat with the enhanced assistant)")
    print("2. Batch Test Mode (test multiple queries)")
    print("3. Demo Mode (see enhanced capabilities)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nSelect mode (1-4): ").strip()
            
            if choice == "1":
                interactive_mode()
                break
            elif choice == "2":
                batch_mode()
                break
            elif choice == "3":
                demo_mode()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
