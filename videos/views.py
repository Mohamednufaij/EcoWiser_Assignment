from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import VideoForm
from .tasks import process_video

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            process_video.delay(video.id) 
# Trigger Celery task
            return redirect('success')
    else:
        form = VideoForm()
    return render(request, 'upload.html', {'form': form})

def success(request):
    return render(request, 'success.html')