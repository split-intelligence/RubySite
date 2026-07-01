from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about-us-v1.html')

def contact(request):
    if request.method == 'POST':
        # Handle form submission here
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # You can save the data to the database or send an email here
    return render(request, 'contact-us.html')




# remove to their apps
def courses(request):
    return render(request, 'courses-v1.html')


def blog(request):
    return render(request, 'blog-grid.html')
