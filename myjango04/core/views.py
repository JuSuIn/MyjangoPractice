from django.contrib import messages
from django.shortcuts import render

# Create your views here.


def index(request):
    messages.debug(request, "디버그 메세지")
    messages.info(request, "정보 메세지")
    messages.success(request, "성공 메세지")
    messages.warning(request, "경고 메세지")
    messages.error(request, "에러 메세지")

    return render(request, template_name="core/index.html")
