import socket
import pickle
import _thread
import sys
import cv2
import numpy as np
import argparse
import cv2
import sys
from django.contrib.staticfiles.templatetags.staticfiles import static
import pickle
import numpy as np
import struct
from django.shortcuts import render
import socketserver
import gzip
from django.views.decorators.gzip import gzip_page
from django.views.decorators import gzip
import cv2
import numpy as np
import threading

from django.http import StreamingHttpResponse,HttpResponseServerError
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
import os
from django.conf import settings
from .forms import UserForm,VideoForm




def index(request):

    if 'socket' in request.session:
        print('yes')
        request.session['socket'].close()

    album_all=Album.objects.all()
    context={'album_all':album_all,    }
    request.session['abc']="abc"
    return render(request,"music/index.html",context)

def details(request,album_id):

    print(request.session['abc'])
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
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def index1(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")



def gen1(request):
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    protxt=PROJECT_ROOT+"/MobileNetSSD_deploy.prototxt.txt"
    model=PROJECT_ROOT+"/MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(protxt, model)
    HOST ="localhost"
    PORT = 8089
    if 'socket' in request.session:
        print("yes")
        print(request.session['socket'])
    else:
        print("no")

    #request.session['socket']=True
    s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn, addr = s.accept()

    data = b''
    payload_size = struct.calcsize("L")

    while True:
        while len(data) < payload_size:
            data += conn.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        ###

        frame = pickle.loads(frame_data)
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > 0.2:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                                             confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

        ret, jpeg= cv2.imencode('.jpg', frame)
        frame=jpeg.tobytes()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def index2(request):

    try:
        return StreamingHttpResponse(gen1(request),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")





