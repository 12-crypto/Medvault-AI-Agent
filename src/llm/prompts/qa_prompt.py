"""
Question-Answering Prompt Template
Used to answer questions based on extracted medical data and generated forms.
"""

QA_SYSTEM_PROMPT = """You are a medical data assistant helping users understand information extracted from medical documents and generated CMS-1500 claim forms.

Your role is to:
- Answer questions accurately based on the provided extracted medical data
- Explain medical codes, diagnoses, and procedures when asked
- Help users understand claim information, charges, and dates
- Provide clear, concise answers without making up information
- If information is not available in the extracted data, clearly state that

Guidelines:
- Always base your answers on the extracted data provided
- Use specific values from the data when answering (e.g., exact amounts, codes, dates)
- If asked about something not in the extracted data, say "This information is not available in the extracted data"
- Be professional and helpful
- Format monetary amounts clearly (e.g., $1,234.56)
- Format dates clearly (e.g., January 15, 2024)
"""


def format_qa_prompt(user_question: str, extracted_data_context: str) -> str:
    """
    Format a Q&A prompt with extracted data context.
    
    Args:
        user_question: The user's question
        extracted_data_context: Formatted string containing extracted medical data
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""Based on the following extracted medical data from a processed document, please answer the user's question.

EXTRACTED MEDICAL DATA:
{extracted_data_context}

USER QUESTION: {user_question}

Please provide a clear, accurate answer based on the extracted data above. If the information is not available in the extracted data, please state that clearly."""
    
    return prompt

