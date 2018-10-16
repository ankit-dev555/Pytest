

from django.http import Http404,HttpResponse
from .models import Album
from .models import video
from django.template import loader
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.views.generic.edit import CreateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import AlbumSerialiser
from django.views.generic import View
from .forms import UserForm,VideoForm

def index(request):
    album_all=Album.objects.all()

    context={'album_all':album_all,    }
    return render(request,"music/index.html",context)

def details(request,album_id):

    try:
        album=Album.objects.get(pk=album_id)


    except:
        raise Http404("album does not exist")


    return render(request,"music/details.html",{'album':album})

def upload(request):
    context={}
    file1=request.FILES
    fs=FileSystemStorage
    fs.save("abc",file1,max_length=None)

    return render(request,"music/upload.html",context)



class videoCreate(CreateView):
    model=video
    fields=['videox','videoname']
    #set name of a field in django manually
    def form_valid(self, form):
        form.instance.videoname="ankit's"
        return super().form_valid(form)



class AlbumList(APIView):
    def get(self,request):
        album=Album.objects.all()
        serializer=AlbumSerialiser(album,many=True)
        return Response(serializer.data)

    def post(self):
        pass


class UserFormView(View):
    form_class=UserForm
    template_name='music/register.html'
    def get(self,request):
        form=self.form_class(None)
        return render(request,self.template_name,{'form':form})


    def post(self,request):
        form=self.form_class(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user.set_password(password)
            user.save()

            #user authentication

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    user = {'user': request.user}
                    return render(request, 'music/index1.html', user)  # or return(redirect('index'),kwargs={'':})

            return render(request,self.template_name,{'form': form})




"""class VideoFormView(View):
    form_class=VideoForm
    template_name='music/upload.html'
    def get(self,request):
        form=self.form_class(None)
        return render(request,self.template_name,{'form':form})


    def post(self,request):
        form=self.form_class(request.POST,request.FILES)
        print("abc")
        print(form.errors)
        if form.is_valid():
            video4=form.save(commit=False)
            
            videoname = form.cleaned_data['videoname']
            video4.save()
            return render(request, self.template_name, {'form': form})
            #user authentication

        return render(request, self.template_name, {'form': form})
"""











