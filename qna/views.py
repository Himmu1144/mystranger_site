from django.shortcuts import render

# Create your views here.
def pika_view(request):
    return render(request, "qna/questions.html")