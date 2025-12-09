from django.db import models
from django.contrib.auth.models import User
import uuid

class ExamSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    is_endless = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.start_time})"

class Question(models.Model):
    exam_session = models.ForeignKey(ExamSession, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    options = models.JSONField()  # Store options as a list of strings
    correct_answer = models.CharField(max_length=255)
    
    def __str__(self):
        return self.text[:50]

class StudentResponse(models.Model):
    exam_session = models.ForeignKey(ExamSession, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.exam_session.user.username} - {self.question.id}"

class ProctoringLog(models.Model):
    exam_session = models.ForeignKey(ExamSession, related_name='logs', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)  # e.g., 'tab_switch', 'face_missing'
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"

class WebcamSnapshot(models.Model):
    exam_session = models.ForeignKey(ExamSession, related_name='snapshots', on_delete=models.CASCADE)
    image_data = models.TextField()  # Base64 encoded image
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Snapshot at {self.timestamp}"
