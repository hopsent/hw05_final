from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """
    Customize page not found template.
    **Context**
    The request's parameter path.
    **Template tags**
    :tag:'load', :tag:'include', :tag:'extends',
    :tag:'block', :tag:'url'
    **Template**
    :template:'core/404.html'
    """
    return render(
        request,
        "core/404.html",
        {"path": request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    """
    Customize server error template.
    **Context**
    The request's parameter path.
    **Template**
    :template:'core/500.html'
    """
    return render(
        request,
        "core/500.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )


def permission_denied(request, exception):
    """
    Customize forbidden template.
    **Template**
    :template:'core/403.html'
    """
    return render(
        request,
        "core/403.html",
        status=HTTPStatus.FORBIDDEN
    )


def csrf_failure(request, reason=""):
    """
    Customize forbidden template for incorrect csrf.
    **Template**
    :template:'core/403csrf.html'
    """
    return render(request, "core/403csrf.html")
