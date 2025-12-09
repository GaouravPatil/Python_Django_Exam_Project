from exam_core.utils import generate_questions
import os
import django
from django.conf import settings

# Configure Django settings manually if needed, or just test the function if it's independent enough.
# However, generate_questions uses genai which depends on env vars loaded by dotenv in utils.py.
# It doesn't seem to depend on Django models directly, so we can run it directly.

print("Testing generate_questions with gemini-1.5-flash...")
try:
    questions = generate_questions("Python", "Easy", count=2)
    print(f"Successfully generated {len(questions)} questions.")
    print("First question:", questions[0]['text'])
except Exception as e:
    print(f"Failed to generate questions: {e}")
