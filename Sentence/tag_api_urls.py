from django.urls import path

from Sentence.api_views import TagView

urlpatterns = [
    path('', TagView.as_view()),
]
