import socket
import pickle
import _thread
import sys
import cv2
import numpy as np
import imutils
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

def index3(request):

    if 'socket' in request.session:
        print('yes')
        request.session['socket'].close()

    return render(request,"music/index_main.html")

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


def detect_face(img):
    # convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))

    # load OpenCV face detector, I am using LBP which is fast
    # there is also a more accurate but slow Haar classifier
    face_cascade = cv2.CascadeClassifier(PROJECT_ROOT+'/opencv-files/haarcascade_frontalface_alt.xml')

    # let's detect multiscale (some images may be closer to camera than others) images
    # result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);

    # if no faces are detected then return original img
    if (len(faces) == 0):
        return None, None

    # under the assumption that there will be only one face,
    # extract the face area
    (x, y, w, h) = faces[0]

    # return only the face part of the image
    return gray[y:y + w, x:x + h], faces[0]


def prepare_training_data(data_folder_path):
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
    dirs = os.listdir(PROJECT_ROOT+"/"+data_folder_path)
    faces = []
    labels = []

    # let's go through each directory and read images within it
    for dir_name in dirs:

        # our subject directories start with letter 's' so
        # ignore any non-relevant directories if any
        if not dir_name.startswith("s"):
            continue;

        # ------STEP-2--------
        # extract label number of subject from dir_name
        # format of dir name = slabel
        # , so removing letter 's' from dir_name will give us label
        label = int(dir_name.replace("s", ""))

        # build path of directory containin images for current subject subject
        # sample subject_dir_path = "training-data/s1"
        subject_dir_path = PROJECT_ROOT+"/"+data_folder_path + "/" + dir_name

        # get the images names that are inside the given subject directory
        subject_images_names = os.listdir(subject_dir_path)

        # ------STEP-3--------
        # go through each image name, read image,
        # detect face and add face to list of faces
        for image_name in subject_images_names:

            # ignore system files like .DS_Store
            if image_name.startswith("."):
                continue;

            # build image path
            # sample image path = training-data/s1/1.pgm
            image_path = subject_dir_path + "/" + image_name
            print(image_path)
            print(label)
            # read image
            image = cv2.imread(image_path)

            # display an image window to show the image

            # detect face
            face, rect = detect_face(image)

            # ------STEP-4--------
            # for the purpose of this tutorial
            # we will ignore faces that are not detected
            if face is not None:
                # add face to list of faces
                faces.append(face)
                # add label for this face
                labels.append(label)
            else:
                print("yes")

    return faces, labels


def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)


# function to draw text on give image starting from
# passed (x, y) coordinates.
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)



def gen2(request):
    subjects = ["","Indresh","ankit","vinayak"]
    faces, labels = prepare_training_data("training-data")
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    print(labels)
    face_recognizer.train(faces, np.array(labels))
    settings_dir = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))

    # load OpenCV face detector, I am using LBP which is fast
    # there is also a more accurate but slow Haar classifier
    face_cascade = cv2.CascadeClassifier(PROJECT_ROOT + '/opencv-files/haarcascade_frontalface_alt.xml')

    HOST = "localhost"
    PORT = 8089
    if 'socket' in request.session:
        print("yes")
        print(request.session['socket'])
    else:
        print("no")

    # request.session['socket']=True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    s.bind((HOST, PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn, addr = s.accept()

    data = b''
    payload_size = struct.calcsize("L")
    (width, height) = (130, 100)

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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (width, height))
            # Try to recognize the face
            prediction = face_recognizer.predict(face_resize)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            if prediction[1] < 500:

                cv2.putText(frame, '% s - %.0f' %
                            (subjects[prediction[0]], prediction[1]), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            else:
                cv2.putText(frame, 'not recognized',
                            (x - 10, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))


        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def index4(request):

    try:
        return StreamingHttpResponse(gen2(request),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")



