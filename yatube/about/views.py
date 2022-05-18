from django.views.generic.base import TemplateView


class AboutAutrhorView(TemplateView):
    """
    Display an infomation about site's owner.
    Static view.
    **Template:**
    :template:'about/author.html'
    """

    template_name = "about/author.html"


class AboutTechView(TemplateView):
    """
    Display an infomation about site's technologies.
    Static view.
    **Template:**
    :template:'about/tech.html'
    """

    template_name = "about/tech.html"
