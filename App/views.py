import cv2
import os
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.files.storage import FileSystemStorage
import random
import string
from PIL import Image as im

def randstring():
    res = ''.join(random.choices(string.ascii_uppercase +string.digits, k = 7))
    return res

def home(request):
    if request.method=="POST" or request.method=="FILES":
        image=request.FILES['image']
        fs=FileSystemStorage()
        files=fs.listdir('')[1]
        for i in files:
            if i.split(".")[-1] in ("jpg","png"):
                fs.delete(i)
    
        filename = fs.save(image.name,image)
        uploaded_file_url = fs.url(filename)
        import cv2
        import numpy as np
        img=cv2.imread(uploaded_file_url.split('/')[-1])
        k=8
        data = np.float32(img).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges  = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 9, 8)
        blurred = cv2.medianBlur(result, 3)
        cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)
        fs=FileSystemStorage()
        fs.delete(filename)
        a=image.name.split('.')[-1]
        k=randstring()
        cv2.imwrite(k+"."+a,cartoon)
        outfile="/"+k+"."+a
        print(type(cartoon))
        return render(request,"home.html",{'output':outfile,"text":"click on photo to download"})

    return render(request,"home.html",{})

def delete(request):
    fs=FileSystemStorage()
    files=fs.listdir('')[1]
    for i in files:
        if i.split(".")[-1] in ("jpg","png"):
            fs.delete(i)
    return HttpResponse("deleted")