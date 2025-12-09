import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.contrib.auth.models import User
from exam_core.models import ExamSession, Question, StudentResponse, ProctoringLog, WebcamSnapshot
from exam_core.utils import generate_questions

def verify_system():
    print("--- Starting Verification ---")
    
    # 1. Create User
    user, created = User.objects.get_or_create(username='testuser')
    if created:
        user.set_password('password')
        user.save()
    print(f"User: {user.username}")

    # 2. Test Question Generation (Mocked if no API key)
    print("\n--- Testing Question Generation ---")
    questions_data = generate_questions("Python", "Easy", count=2)
    print(f"Generated {len(questions_data)} questions.")
    if questions_data:
        print(f"Sample: {questions_data[0]['text']}")

    # 3. Create Exam Session
    print("\n--- Creating Exam Session ---")
    session = ExamSession.objects.create(
        user=user,
        subject="Python",
        difficulty="Easy",
        total_questions=len(questions_data)
    )
    print(f"Session ID: {session.id}")

    # 4. Save Questions
    for q_data in questions_data:
        Question.objects.create(
            exam_session=session,
            text=q_data['text'],
            options=q_data['options'],
            correct_answer=q_data['correct_answer']
        )
    print(f"Saved {session.questions.count()} questions to DB.")

    # 5. Simulate Answering
    print("\n--- Simulating Answers ---")
    q1 = session.questions.first()
    # Correct answer
    StudentResponse.objects.create(
        exam_session=session,
        question=q1,
        selected_answer=q1.correct_answer,
        is_correct=True
    )
    print(f"Answered Q1 correctly.")

    # 6. Simulate Proctoring Log
    print("\n--- Simulating Proctoring Log ---")
    ProctoringLog.objects.create(
        exam_session=session,
        event_type="tab_switch",
        details="User switched to another tab"
    )
    print(f"Logged tab switch event.")

    # 7. Simulate Snapshot
    print("\n--- Simulating Snapshot ---")
    WebcamSnapshot.objects.create(
        exam_session=session,
        image_data="data:image/jpeg;base64,fakebased64data"
    )
    print("Saved snapshot.")

    # 8. Complete Exam
    print("\n--- Completing Exam ---")
    session.is_completed = True
    session.score = 1
    session.save()
    print(f"Exam completed. Score: {session.score}")

    print("\n--- Verification Successful ---")

if __name__ == "__main__":
    verify_system()
