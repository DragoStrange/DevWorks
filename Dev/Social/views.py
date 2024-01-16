from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse,resolve
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *
import json
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request,'home.html')

# List Posts in Feed
@login_required
def feed(request):
    user = request.user
    posts = Stream.objects.filter(user=user)
    group_ids = []
    for post in posts:
        group_ids.append(post.post_id)
    post_items = Post.objects.filter(id__in=group_ids).all().order_by('-posted')
    #Checking if previously liked
    for post in post_items:
        post.user_has_liked = post.likes.filter(id=user.id).exists()

    context = {'post_items': post_items}
    return render(request, 'feed.html', context)

def frontpage(request):
    return render(request,'frontpage.html')

#Signup
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        fname = request.POST['fname']
        username = request.POST['username']
        pass1 = request.POST['pass1']
        myuser = User.objects.create_user(username,email,pass1)
        list1 = fname.split(" ")
        firstn = list1[0]
        lastn = list1[1]
        myuser.first_name = firstn
        myuser.last_name = lastn
        
        myuser.save()

        messages.success(request, "Your account has been succesfully created.")

        return redirect('signin')

    return render(request,'signup.html')

#Signin
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fn = user.first_name
            return render(request, 'frontpage.html', {'fn': fn})

        else:
            messages.error(request, "Bad Credentials!")
            return redirect('frontpage')

    return render(request,'signin.html')

#Signout 
def signout(request):
    logout(request)
    messages.success(request, "Logged out Successfully")
    return redirect('frontpage')

#Create New Post
@login_required
def NewPost(request):
    user = request.user.id
    tags_objs = []

    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = request.POST.get('caption')
            tag_form = form.cleaned_data.get('tag')
            tags_list = list(tag_form.split(' '))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            p, created = Post.objects.get_or_create(picture=picture, caption=caption, user_id=user)
            p.tag.set(tags_objs)
            p.save()
        return redirect('feed')
    else:
        form = NewPostForm()
    context = {
        'form': form
    }
    return render(request, 'newpost.html', context)

#Detailed Post page
def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post' : post
    }
    return render(request, 'post-details.html', context)


#Tag filtering posts
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tag=tag).order_by('-posted')
    context = {
        'tag' : tag,
        'posts' : posts
    }
    return render(request, 'tags.html', context)

#Like with Ajax
def like(request):
    data = json.loads(request.body)
    id = data["id"]
    post = Post.objects.get(id=id)
    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            checker = 0
        else:
            post.likes.add(request.user)
            checker = 1
    likes = post.likes.count()
    info = {
        "check": checker,
        "num_of_likes": likes
    }
    return JsonResponse(info, safe=False)

#Savepost
def saved(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)
    if profile.saved.filter(id=post_id).exists():
        profile.saved.remove(post)
    else:
        profile.saved.add(post)
    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


def test(request):
    user = request.user
    posts = Post.objects.all().order_by('-posted')
    return render(request,'test.html', {'post_items':posts})


def post_comments(request,id):
    a=Post.objects.get(pk=id)
    b=a.comments_set.all()
    return render(request,'Post/comment.html',{'post':a,'comment':b})

#Profile
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')
    else:
        posts = profile.saved.all()
    
    #Tracking Profile Stats
    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    follower_count = Follow.objects.filter(following=user).count()
    
    #Follow status
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()
    #pagination
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)
    context = {
        'posts_paginator' : posts_paginator,
        'profile' : profile,
        'posts' : posts,
        'url_name' : url_name,
        'post_count' : post_count,
        'following_count' : following_count,
        'follower_count' : follower_count,
        'follow_status' : follow_status
    }
    return render(request, 'profile.html', context)

#Follow function
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)
    try:
        f, created = Follow.objects.get_or_create(follower=user, following=following)
        if int(option) == 0 :
            f.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
        else:
            posts = Post.objects.filter(user=following)[:10]

            with transaction.atomic():
                for post in posts:
                    stream = Stream(post=post, user=user, date=post.posted, following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('profile', args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))

#Edit profile
def editProfile(request):
    user = request.user
    profile = Profile.objects.get(user__id=user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.image = form.cleaned_data.get('picture')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.bio = form.cleaned_data.get('bio')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.save()
            return redirect('profile')
    else:
        form = EditProfileForm()
    context = {
        'form' : form,
    }
    return render(request, 'edit-profile.html', context)


# def createtweet(request):
#     if not request.user.is_authenticated:
#         redirect('signin')
#     if request.method=="POST":
#         form=TweetForm(request.POST)
#         if form.is_valid():
#             twt_form=form.save(commit=False)
#             twt_form.user=request.user
#             twt_form.save()
#             return redirect(frontpage)
#         else:
#             return HttpResponse("Form not validated")
#     form=TweetForm()
#     return render(request,newtweet.html',{'form':form})


# def edittweet(request,id):
#     if not request.user.is_authenticated:
#         redirect('signin')
#     r=Tweet.objects.get(id=id)
#     if request.method=="POST":
#         form=TweetForm(request.POST,instance=r)
#         if form.is_valid():
#             twt_form=form.save(commit=False)
#             twt_form.user=request.user
#             twt_form.save()
#             return redirect(userprofile)
#         else:
#             return HttpResponse("Form not validated")
#     form=TweetForm(instance=r)
#     return render(request,edittweet.html',{'form':form})


# def deletetweet(request,id):
#     if not request.user.is_authenticated:
#         redirect('/user/login')    
#     if request.method=="POST":
#         twt=Tweet.objects.get(id=id)
#         twt.delete()
#         return redirect(userprofile)
        
#     q=Tweet.objects.get(id=id)
#     return render(request,'Tweet/deletetweet.html',{'context':q})


# def tweet_replies(request,id):
#     a=Tweet.objects.get(id=id)
#     b=reversed(a.reply_set.all())
#     return render(request,'Tweet/demo.html',{'tweet':a,'reply':b})
