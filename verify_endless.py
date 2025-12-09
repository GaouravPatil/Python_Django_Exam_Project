import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.contrib.auth.models import User
from exam_core.models import ExamSession, Question
from django.test import RequestFactory
from exam_core.views import GetNextQuestionView

def verify_endless_mode():
    print("--- Starting Endless Mode Verification ---")
    
    user = User.objects.get(username='testuser')
    
    # 1. Create Endless Session
    print("\n--- Creating Endless Session ---")
    session = ExamSession.objects.create(
        user=user,
        subject="Python",
        difficulty="Easy",
        total_questions=1,
        is_endless=True
    )
    print(f"Session ID: {session.id}, Is Endless: {session.is_endless}")

    # 2. Test GetNextQuestionView
    print("\n--- Testing GetNextQuestionView ---")
    factory = RequestFactory()
    data = {'session_id': str(session.id)}
    request = factory.post('/api/next_question/', data=json.dumps(data), content_type='application/json')
    request.user = user
    
    view = GetNextQuestionView.as_view()
    response = view(request)
    
    print(f"Response Status: {response.status_code}")
    if response.status_code == 200:
        content = json.loads(response.content)
        print(f"New Question ID: {content['id']}")
        print(f"New Total Questions: {content['total_questions']}")
        
        # Verify DB update
        session.refresh_from_db()
        print(f"DB Total Questions: {session.total_questions}")
        if session.total_questions == 2:
            print("SUCCESS: Session updated correctly.")
        else:
            print("FAILURE: Session count mismatch.")
    else:
        print(f"Error: {response.content}")

    print("\n--- Verification Finished ---")

if __name__ == "__main__":
    verify_endless_mode()
