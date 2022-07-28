import mimetypes
from django.shortcuts import render,redirect
from django.http import HttpResponse
import PyPDF2
from gtts import gTTS
from django.contrib.auth.models import User
from pdfconv.functions import handle_uploaded_file
from pdfconv.models import UserPDF
from .forms import NewUserForm, PDFForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout 

def home(request):
    return render(request,'home.html')

def usersignup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("home")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="usersignup.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("user_home")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("home")


def user_home(request):
    return render(request, 'user_home.html')
def user_pdf_upload(request):
    if request.method == 'POST':  
        student = PDFForm(request.POST, request.FILES)  
        if student.is_valid(): 
            user_pdf=UserPDF() 
            user_instance=User.objects.get(id=request.user.id)
            user_pdf.user = user_instance
            user_pdf.filename = request.FILES['file'].name
            user_pdf.save()
            handle_uploaded_file(request.FILES['file'])  
            return redirect("pdf_convert_to_audio")  
    else:  
        student = PDFForm()  
        return render(request,"user_pdf_upload.html",{'pdf_upload':student})  
def pdf_convert_to_audio(request):
    user_file_name=UserPDF.objects.values('filename').filter(user=request.user.id)  
    # path of the PDF file
    path = open('pdfconv/static/upload/'+user_file_name[0]['filename'], 'rb')        
    # creating a PdfFileReader object
    pdfReader = PyPDF2.PdfFileReader(path)        
    # the page with which you want to start
    # this will read the page of 25th page.
    text =''
    count=pdfReader.numPages
    for i in range(count):
        from_page = pdfReader.getPage(i)
        # # extracting the text from the PDF
        text += from_page.extractText()        
    # reading the text
    tts = gTTS(text)
    tts.save("pdfconv/static/audio/"+user_file_name[0]['filename']+"converted.mp3")
    path = open("pdfconv/static/audio/"+user_file_name[0]['filename']+"converted.mp3", 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type("pdfconv/static/audio/"+user_file_name[0]['filename']+"converted.mp3")
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    filename=user_file_name[0]['filename']+"converted.mp3"
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response
    