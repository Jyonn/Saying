from django.urls import path

from Sentence.api_views import SentenceView

urlpatterns = [
    path('', SentenceView.as_view()),
]
