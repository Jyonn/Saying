from django.urls import path

from Sentence.api_views import SentenceView, TagView

urlpatterns = [
    path('sentence', SentenceView.as_view()),
    path('tag', TagView.as_view()),
]
