from SmartDjango import E
from django.views import View


class ErrorView(View):
    @staticmethod
    def get(request):
        return E.all()
