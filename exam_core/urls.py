from django.urls import path
from .views import (
    DashboardView, ExamSetupView, ExamView, SaveAnswerView, 
    LogActivityView, UploadSnapshotView, ResultView, GetNextQuestionView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('setup/', ExamSetupView.as_view(), name='exam_setup'),
    path('exam/<uuid:session_id>/', ExamView.as_view(), name='exam_interface'),
    path('api/save_answer/', SaveAnswerView.as_view(), name='save_answer'),
    path('api/log_activity/', LogActivityView.as_view(), name='log_activity'),
    path('api/upload_snapshot/', UploadSnapshotView.as_view(), name='upload_snapshot'),
    path('api/next_question/', GetNextQuestionView.as_view(), name='next_question'),
    path('result/<uuid:session_id>/', ResultView.as_view(), name='result'),
]
