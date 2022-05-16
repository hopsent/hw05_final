from django.views.generic.base import TemplateView


class AboutAutrhorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
