from client import OllamaClient
from models import EmailData
from pipeline import EmailProcessor
from log import logger

from datetime import datetime




def main():
    """Example usage of the email responder"""
    
    # Initialize Ollama client
    llm_client = OllamaClient(model="llama3.2")  # Change model as needed
    
    # Initialize email processor
    email_processor = EmailProcessor(llm_client)
    
    # Example email data
    sample_email = EmailData(
        sender="customer@example.com",
        subject="Issue with my recent order",
        content="Hi, I ordered a product last week but it hasn't arrived yet. The tracking shows it's been stuck in transit for 3 days. Can you help me figure out what's going on? This is really frustrating as I needed this for an important meeting.",
        timestamp=datetime.now()
    )
    
    try:
        # Process the email using the modular processor
        processed_email = email_processor.process_email(sample_email)
        
        # Display results
        print("\n" + "="*50)
        print("EMAIL PROCESSING RESULTS")
        print("="*50)
        print(f"From: {processed_email.sender}")
        print(f"Subject: {processed_email.subject}")
        print(f"Classification: {processed_email.urgency}")
        print(f"Query Type: {processed_email.query_type}")
        print(f"Needs Follow-up: {processed_email.needs_followup}")
        print("\nGenerated Response:")
        print("-" * 20)
        print(processed_email.response)
        
    except Exception as e:
        logger.error(f"Email processing failed: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()