from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import ExamSession, Question, StudentResponse, ProctoringLog, WebcamSnapshot
from .utils import generate_questions
import json
import base64
from django.core.files.base import ContentFile

class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            # Quick hack to auto-login a test user for demo purposes if not logged in
            user, created = User.objects.get_or_create(username='student')
            if created:
                user.set_password('password')
                user.save()
            login(request, user)
        
        exams = ExamSession.objects.filter(user=request.user).order_by('-start_time')
        return render(request, 'dashboard.html', {'exams': exams})

class ExamSetupView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'exam_setup.html')

    def post(self, request):
        subject = request.POST.get('subject')
        difficulty = request.POST.get('difficulty')
        mode = request.POST.get('mode') # 'normal' or 'endless'
        
        is_endless = (mode == 'endless')
        total_questions = 5 if not is_endless else 1 # Start with 1 for endless
        
        # Create Exam Session
        session = ExamSession.objects.create(
            user=request.user,
            subject=subject,
            difficulty=difficulty,
            total_questions=total_questions,
            is_endless=is_endless
        )
        
        # Generate Questions
        # For endless, we can start with 1 or 5. Let's start with 1 to test dynamic loading quickly.
        count = 1 if is_endless else 5
        questions_data = generate_questions(subject, difficulty, count=count)
        for q_data in questions_data:
            Question.objects.create(
                exam_session=session,
                text=q_data['text'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer']
            )
            
        return redirect('exam_interface', session_id=session.id)

class ExamView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        if session.is_completed:
            return redirect('result', session_id=session.id)
            
        questions = session.questions.all()
        return render(request, 'exam_interface.html', {'session': session, 'questions': questions})

    def post(self, request, session_id):
        # Handle Exam Submission
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        session.is_completed = True
        
        # Calculate Score
        score = 0
        responses = session.responses.all()
        for response in responses:
            if response.is_correct:
                score += 1
        
        session.score = score
        session.save()
        
        return redirect('result', session_id=session.id)

class SaveAnswerView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        question = get_object_or_404(Question, id=question_id, exam_session=session)
        
        # Check correctness
        is_correct = (selected_answer == question.correct_answer)
        
        # Update or Create Response
        StudentResponse.objects.update_or_create(
            exam_session=session,
            question=question,
            defaults={'selected_answer': selected_answer, 'is_correct': is_correct}
        )
        
        return JsonResponse({'status': 'saved'})

class LogActivityView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        session_id = data.get('session_id')
        event_type = data.get('event_type')
        details = data.get('details')
        
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        ProctoringLog.objects.create(
            exam_session=session,
            event_type=event_type,
            details=details
        )
        
        return JsonResponse({'status': 'logged'})

class UploadSnapshotView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        session_id = data.get('session_id')
        image_data = data.get('image_data') # Base64 string
        
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        WebcamSnapshot.objects.create(
            exam_session=session,
            image_data=image_data
        )
        
        return JsonResponse({'status': 'uploaded'})

class GetNextQuestionView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        
        if not session.is_endless:
            return JsonResponse({'error': 'Not an endless session'}, status=400)
            
        # Generate 1 new question
        q_data_list = generate_questions(session.subject, session.difficulty, count=1)
        if not q_data_list:
             return JsonResponse({'error': 'Failed to generate question'}, status=500)
             
        q_data = q_data_list[0]
        question = Question.objects.create(
            exam_session=session,
            text=q_data['text'],
            options=q_data['options'],
            correct_answer=q_data['correct_answer']
        )
        
        # Update total questions count
        session.total_questions += 1
        session.save()
        
        return JsonResponse({
            'id': question.id,
            'text': question.text,
            'options': question.options,
            'total_questions': session.total_questions
        })

class ResultView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        return render(request, 'result.html', {'session': session})
