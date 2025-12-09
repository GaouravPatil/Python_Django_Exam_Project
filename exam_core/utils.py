import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def generate_questions(subject, difficulty, count=5):
    """
    Generates multiple-choice questions using Gemini API.
    """
    if not API_KEY:
        # Fallback for testing if no API key is present
        return [
            {
                "text": f"Sample Question 1 about {subject} ({difficulty})",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A"
            }
        ] * count

    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Generate {count} multiple-choice questions on the subject '{subject}' with '{difficulty}' difficulty.
    Return the response strictly as a JSON list of objects. 
    Each object must have the following keys:
    - "text": The question text.
    - "options": A list of 4 options.
    - "correct_answer": The correct option string (must be one of the options).
    
    Do not include any markdown formatting or explanations. Just the JSON.
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up potential markdown code blocks
        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        elif text_response.startswith("```"):
            text_response = text_response[3:-3]
            
        questions = json.loads(text_response)
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Fallback to mock questions
        return [
            {
                "text": f"Mock Question {i+1} about {subject} ({difficulty}) - API Unavailable",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A"
            } for i in range(count)
        ]
