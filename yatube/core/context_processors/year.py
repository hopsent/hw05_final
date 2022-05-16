from datetime import datetime


def year(request):
    # Adds variable with current year
    return {"year": datetime.now().year}
