from django.views.generic import TemplateView

class HelloDjango(TemplateView):
    template_name = 'home.html'
