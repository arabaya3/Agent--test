#!/usr/bin/env python3

from email_agent_example import EmailAgent
import time

def test_email_agent():
    print("Testing Email Agent")
    print("=" * 60)
    
    agent = EmailAgent()
    
    print("Checking server health...")
    if agent.check_server_health():
        print("Server is running and healthy")
    else:
        print("Server is not available. Please start the Flask server first.")
        return
    
    print("\n" + "=" * 60)
    print("Testing Email Queries")
    print("=" * 60)
    
    test_queries = [
        "Find emails from executive.assistant@menadevs.io",
        "Show me emails about meeting",
        "Get emails with subject project",
        "Find messages about budget",
        "Show emails from noreply@microsoft.com"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        start_time = time.time()
        response = agent.answer_query(query)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Response:")
        print(response)
        print("-" * 40)
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Email Agent Testing Complete")
    print("=" * 60)

def interactive_mode():
    print("Email Agent Interactive Mode")
    print("=" * 60)
    print("Type 'quit' to exit")
    print("=" * 60)
    
    agent = EmailAgent()
    
    if not agent.check_server_health():
        print("Server is not available. Please start the Flask server first.")
        return
    
    while True:
        try:
            query = input("\nEnter your email query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                print("Please enter a query.")
                continue
            
            print("Searching...")
            response = agent.answer_query(query)
            print(f"Result:\n{response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        test_email_agent()
