import json
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models.expressions import F
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import *

def follow (request):
    followedpost = Follow.objects.filter(follower = request.user.id).values_list('followed')
    if not followedpost:
        return render(request, "network/follow.html", {
            "msg": "you are not following anyone at this time",
    })
    else:
        post = Post.objects.filter(user__in = followedpost).annotate(liked_count=Count('liked_post', distinct=True)).annotate(comment_count=Count('comment', distinct=True)).order_by('-id')
        paginator = Paginator(post, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/follow.html", {
            "post": post,
            'page_obj': page_obj,
        })

@csrf_exempt 
def postlikes (request, post_id):
    if request.method == "GET":
            likes = Like.objects.filter(post = post_id).values('user')
            return JsonResponse({'likeduser': list(likes)})
    
    elif request.method == "PUT":
        if request.user.is_authenticated:
            data = json.loads(request.body)
            userid = data.get("userid", "")
            postid = data.get("postid", "")
            liked = data.get("liked", "")
            if liked == True:
                Like.objects.filter(user = userid, post = postid).delete()
                return JsonResponse({
                    "message": "disliked"}, status=201
                )
            else:
                addlike = Like(user_id = userid, post_id = post_id)
                addlike.save()
                return JsonResponse({
                    "message": "liked"}, status=201
                )
        else:
            return JsonResponse({
                "error": "Login required.",
            }, status=400)
    

@csrf_exempt 
def editpost (request, post_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            try:
                post = Post.objects.get(pk = post_id)
            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found."}, status=404)
            
            post = Post.objects.filter(user = request.user, pk = post_id).count()
            if post < 1:
                return JsonResponse({"error": "Invalid user."}, status=400)
            else:
                post = Post.objects.get(pk = post_id)
                return JsonResponse(post.serialize())
        elif request.method == "PUT":
            data = json.loads(request.body)
            posttext = data.get("post", "")
            Post.objects.filter(user = request.user, pk = post_id).update(post = posttext)
            return JsonResponse({
                "message": "post saved successfully."}, status=201
            )
        else:
            return JsonResponse({
                "error": "GET or PUT request required."
            }, status=400)
    else:
        return JsonResponse({
                "error": "Login required."
            }, status=400)

def profile (request):
    post = Post.objects.filter(user = request.user.id).annotate(liked_count=Count('liked_post', distinct=True)).annotate(comment_count=Count('comment', distinct=True)).order_by('-id')
    postcount = Post.objects.filter(user=request.user).count()
    followcount = Follow.objects.filter(followed = request.user.id).count()
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "post": post,
        "follows": followcount,
        "postcount": postcount,
        "page_obj": page_obj,
    })

@csrf_exempt    
def comment (request, post_id):
    postbyid = Post.objects.annotate(liked_count=Count('liked_post', distinct=True)).annotate(comment_count=Count('comment', distinct=True)).filter(id = post_id)
    commentlist = Comment.objects.filter(post = post_id).order_by('-id')
    if request.method == "POST":
        leavecomment = request.POST["leavecomment"]
        lcomment = Comment(user = request.user, comment = leavecomment, post_id = post_id)
        lcomment.save()
        return render(request, "network/comment.html", {
            "post": postbyid,
            "post_id": post_id,
            "commentlist": commentlist,
        })
    else:
        paginator = Paginator(commentlist, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/comment.html", {
            "post": postbyid,
            "post_id": post_id,
            "commentlist": commentlist,
            "page_obj": page_obj,
        })

def usr (request, usr):
    if request.method == "POST":
        if 'followbutton' in request.POST:
            id = User.objects.filter(username = usr).values('id')[0]['id']
            usrf = User.objects.get(username = usr)
            followcount = Follow.objects.filter(follower=request.user.id, followed=id).count()
            if followcount < 1:
                followed = Follow(follower = request.user, followed = usrf)
                followed.save()
                messages.success(request, 'You are now follow {usr}' )
                return HttpResponseRedirect(reverse("usr", args=(usr,)))
            else:
                followed = Follow.objects.filter(follower=request.user.id, followed=id)
                followed.delete()
                messages.success(request, 'You are now unfollow {usr}')
                return HttpResponseRedirect(reverse("usr", args=(usr,)))
    
    else:    
        #valid user name?
        usrcheck = User.objects.filter(username = usr).count()
        if usrcheck < 1:
            return render(request, "network/notfound.html", {
            "usr": usr,
        })
        
        id = User.objects.filter(username = usr).values('id')[0]['id']
        followed = Follow.objects.filter(follower=request.user.id, followed=id).count()
        post = Post.objects.filter(user = id).annotate(liked_count=Count('liked_post', distinct=True)).annotate(comment_count=Count('comment', distinct=True)).order_by('-id')
        postcount = Post.objects.filter(user = id).count()
        followcount = Follow.objects.filter(followed = id).count()
        followed = Follow.objects.filter(follower=request.user.id, followed=id).count()
        email = User.objects.filter(username = usr).values('email')[0]['email']
        paginator = Paginator(post, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if id == request.user.id:
            followed = 2
        elif followed > 0:
            followed = True
        else:
            followed = False


        return render(request, "network/user.html", {
            "post": post,
            "follows": followcount,
            "followed": followed,
            "postcount": postcount,
            "usr": usr,
            "email": email,
            "followed": followed,
            "page_obj": page_obj,
        })

@csrf_exempt
def index(request):
    post = Post.objects.annotate(liked_count=Count('liked_post', distinct=True)).annotate(comment_count=Count('comment', distinct=True)).order_by('-id')
    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.method == "POST":
        leavepost = request.POST["leavepost"]
        lpost = Post(user = request.user, post = leavepost)
        lpost.save()
        return render(request, "network/index.html", {
            "post": post,
            'page_obj': page_obj
        })
    else:
        return render(request, "network/index.html", {
            "post": post,
            'page_obj': page_obj,
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
