from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm,UserForm,MyUserCreationForm
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.contrib.auth import get_user_model
User  = get_user_model()

# Create your views here.

#rooms=[
#    {'id':1,'name':'lets learn python'},
#    {'id':2,'name':'Django'},
#    {'id':3,'name':'Java'},
#]

def loginPage(request):
      
    page='login'
    
    #if request.method =='POST':
    #    username = request.POST.get('username')
    #    password = request.POST.get('password')
        
    #    user = auth.authenticate(username = username ,password = password)
        
    #    if user is not None :
    #        auth.login(request,user)
    #        return redirect('home')
    #    else:
    #        messages.info(request,"Invalid credintials")
    #        return redirect('login')
    #else:
    #    context = {'page':page} #'page':page
    #    return render(request,'base/login_register.html',context)
    
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=="POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user =User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist')
        
        user = auth.authenticate(request,email=email,password=password)
        
        if user is not None:
                   
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Username OR password is Invalid')
    
    context = {'page':page} #'page':page
    return render(request,'base/login_register.html',context)

def registerPage(request):
    
    page='register'
    
    #if request.method =='POST':
    #    username = request.POST['username']
    #    password1 = request.POST['password1']
    #    password2 = request.POST['password2']
    #    if password1 ==password2:
    #        if User.objects.filter(username=username).exists():
    #            messages.info(request,'Username TAKEN....')
    #            return redirect('register')
            
            
    #        else:
    #            user = User.objects.create_user(username = username,password = password1)
    #            user.save()
    #            return redirect('home')
    #    else:
    #        messages.info(request,'Password NOT matching....')
            
    #    return redirect('navbar')
    #else:
    #    return render(request,'base/login_register.html')
    
    
    
    
    
    form = MyUserCreationForm()
    
    if request.method =="POST":
        form =MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            
            user.save()
            auth.login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    context={'form':form}  
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    auth.logout(request)
    return redirect('home')

def home(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms= Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages =Message.objects.filter(Q(room__topic__name__icontains=q))
    context= {'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method =='POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context= {'room':room,'room_messages': room_messages,'participants':participants}
    return render(request,'base/room.html',context)


def userProfile(request,pk):
    user=User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method=="POST":
        topic_name =  request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        
        Room.objects.create(
            host = request.user,
            topic = topic ,
            name = request.POST.get('name'),
            description = request.POST.get('description')
            )
        
        return redirect('home')
    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form= RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user !=room.host:
        return HttpResponse("You are not allowed here")
    
    if request.method=='POST':
        topic_name =  request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')    
        room.topic = topic  
        room.description = request.POST.get('description')
        room.save()    
        return redirect('home')   
    context={'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)
@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    
    if request.user !=room.host:
        return HttpResponse("You are not allowed here")
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room })




@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    
    if request.user !=message.user:
        return HttpResponse("You are not allowed here")
    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message })

@login_required(login_url = 'login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method =='POST':
        form = UserForm(request.POST,request.FILES, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    
    context={'form':form}
    return render(request,'base/update-user.html',context)
    
    
def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') !=None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request,'base/activity.html' ,{'room_messages':room_messages})