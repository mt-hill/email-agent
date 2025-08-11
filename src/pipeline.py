from src.log import logger
from client import OllamaClient
from models import EmailData


class EmailProcessor:
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
        self.valid_urgencies = ["low", "medium", "high"]
        self.valid_query_types = ["billing", "shipping", "bug", "account", "general", "spam"]
        
        # Department routing mapping
        self.department_mapping = {
            "billing": "Finance Department",
            "shipping": "Logistics Department", 
            "bug": "Technical Support",
            "account": "Customer Service",
            "general": "Customer Service",
            "spam": "Auto-Filter"
        }
    
    def classify_urgency(self, email_data: EmailData) -> str:
        """Step 1a: Classify urgency level"""
        logger.info(f"Classifying urgency for email from {email_data.sender}")
        
        prompt = f"""Classify the urgency level of this email as: low, medium, or high.

Consider these factors:
- Time-sensitive language (urgent, ASAP, immediately, deadline)
- Impact on business or customer (service down, payment issues, account locked)
- Emotional tone (frustrated, angry, desperate)

Email Subject: {email_data.subject}
Email Content: {email_data.content}

Respond with only one word: low, medium, or high"""
        
        try:
            urgency = self.llm_client.generate(prompt).lower().strip()
            
            if urgency not in self.valid_urgencies:
                logger.warning(f"Invalid urgency '{urgency}', defaulting to 'medium'")
                urgency = "medium"
                
            logger.info(f"Email urgency classified as: {urgency}")
            return urgency
            
        except Exception as e:
            logger.error(f"Urgency classification failed: {e}")
            return "medium"  # Explicit fallback
    
    def classify_query_type(self, email_data: EmailData) -> str:
        """Step 1b: Classify query type for department routing"""
        logger.info(f"Classifying query type for email from {email_data.sender}")
        
        prompt = f"""Classify this email into one of these categories: billing, shipping, bug, account, general, or spam.

Categories explained:
- billing: Payment issues, invoices, charges, refunds, pricing questions
- shipping: Delivery problems, tracking, packaging, shipping costs
- bug: Technical issues, software problems, website errors, app crashes
- account: Login issues, password resets, profile changes, account settings
- general: Product questions, support requests, feedback that don't fit other categories
- spam: Promotional content, irrelevant messages, suspicious emails

Email Subject: {email_data.subject}
Email Content: {email_data.content}

Respond with only one word: billing, shipping, bug, account, general, or spam"""
        
        try:
            query_type = self.llm_client.generate(prompt).lower().strip()
            
            if query_type not in self.valid_query_types:
                logger.warning(f"Invalid query type '{query_type}', defaulting to 'general'")
                query_type = "general"
                
            logger.info(f"Email query type classified as: {query_type}")
            return query_type
            
        except Exception as e:
            logger.error(f"Query type classification failed: {e}")
            return "general"  # Explicit fallback
    
    def determine_department(self, query_type: str) -> str:
        """Step 1c: Route to appropriate department based on query type"""
        department = self.department_mapping.get(query_type, "Customer Service")
        logger.info(f"Email routed to: {department}")
        return department
    
    def generate_response(self, email_data: EmailData) -> str:
        """Step 2: Generate response based on urgency and query type"""
        logger.info(f"Generating {email_data.urgency} urgency, {email_data.query_type} response")
        
        if email_data.query_type == "spam":
            return ""  # No response for spam
        
        # Build context-aware prompt based on both urgency and type
        urgency_context = {
            "high": "This is a high-priority email that requires immediate attention and swift action.",
            "medium": "This is a standard priority email that should be addressed promptly.",
            "low": "This is a low-priority email that can be addressed in normal timeframes."
        }
        
        type_context = {
            "billing": "This is a billing-related inquiry. Be specific about payment processes and next steps.",
            "shipping": "This is a shipping-related inquiry. Provide tracking information and delivery expectations.",
            "bug": "This is a technical issue. Offer troubleshooting steps and escalation if needed.",
            "account": "This is an account-related inquiry. Focus on security and account management steps.",
            "general": "This is a general inquiry. Be helpful and comprehensive in your response."
        }
        
        prompt = f"""Write a professional email response with the following context:

{urgency_context.get(email_data.urgency, urgency_context["medium"])}
{type_context.get(email_data.query_type, type_context["general"])}

Original Email:
Subject: {email_data.subject}
Content: {email_data.content}

Department: {email_data.department}
Urgency Level: {email_data.urgency}

The response should:
- Match the urgency level (high=immediate action, medium=prompt response, low=standard response)
- Address the specific type of inquiry appropriately
- Include relevant department-specific information
- Provide clear next steps
- Be professional and helpful"""
        
        try:
            response = self.llm_client.generate(prompt)
            logger.info("Response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"Thank you for your email. Your {email_data.query_type} inquiry has been received and will be handled by our {email_data.department}. We will respond shortly."
    
    def should_schedule_followup(self, email_data: EmailData) -> bool:
        """Step 3: Determine if follow-up is needed based on urgency and type"""
        high_urgency = email_data.urgency == "high"
        critical_types = ["bug", "billing", "account"]
        critical_type = email_data.query_type in critical_types
        
        needs_followup = high_urgency or critical_type
        
        if needs_followup:
            logger.info(f"Follow-up scheduled for {email_data.urgency} urgency {email_data.query_type} email")
        
        return needs_followup
    
    def process_email(self, email_data: EmailData) -> EmailData:
        """
        Main pipeline with dual classification:
        Input → Urgency Classification → Query Type Classification → Department Routing → Response Generation → Follow-up Check → Output
        """
        logger.info(f"Processing email from {email_data.sender}: {email_data.subject}")
        
        # Step 1a: Classify urgency
        email_data.urgency = self.classify_urgency(email_data)
        
        # Step 1b: Classify query type
        email_data.query_type = self.classify_query_type(email_data)
        
        # Step 1c: Determine department routing
        email_data.department = self.determine_department(email_data.query_type)
        
        # Step 2: Generate context-aware response
        email_data.response = self.generate_response(email_data)
        
        # Step 3: Check if follow-up is needed
        email_data.needs_followup = self.should_schedule_followup(email_data)
        
        logger.info("Email processing complete")
        return email_data