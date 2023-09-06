from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.contrib.auth.decorators import login_required


from .models import User, Post, Follow, Like


def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()

    paginator = Paginator(all_posts, 3)
    page_number = request.GET.get('page')
    page_posted = paginator.get_page(page_number)
    
    all_likes = Like.objects.all()

    who_liked = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked.append(like.post.id)
    except: 
        who_liked = []


    return render(request, "network/index.html", {
        "all_posts" : all_posts,
        "page_posted": page_posted,
        "who_liked" : who_liked
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

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

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

def new_post(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followed = Follow.objects.filter(user_followed=user)

    try:
        check_follow = followed.filter(user=User.objects.get(pk=request.user.id))
        if len(check_follow) != 0:
            is_following = True
        else:
            is_following = False
    except:
        is_following = False

    paginator = Paginator(all_posts, 3)
    page_number = request.GET.get('page')
    page_posted = paginator.get_page(page_number)

    all_likes = Like.objects.all()

    who_liked = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked.append(like.post.id)
    except: 
        who_liked = []

    return render(request, "network/profile.html", {
        "all_posts" : all_posts,
        "page_posted": page_posted,
        "username":user.username,
        "following" : following,
        "followed" : followed,
        "is_following" : is_following,
        "user_profile" : user,
        "who_liked" : who_liked
    })


def follow(request):
    user_follow = request.POST['userfollow']
    current_user = User.objects.get(pk=request.user.id)
    user_follow_data = User.objects.get(username=user_follow)
    f = Follow(user=current_user, user_followed=user_follow_data)
    f.save()
    user_id = user_follow_data.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))


def unfollow(request):
    user_follow = request.POST['userfollow']
    current_user = User.objects.get(pk=request.user.id)
    user_follow_data = User.objects.get(username=user_follow)
    f= Follow.objects.get(user=current_user, user_followed=user_follow_data)
    f.delete()
    user_id = user_follow_data.id
    return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_id}))

def following (request):
    current_user = User.objects.get(pk=request.user.id)
    user_people = Follow.objects.filter(user=current_user)
    all_posts = Post.objects.all().order_by('id').reverse()

    people_posts = []

    for post in all_posts:
        for person in user_people:
            if person.user_followed == post.user:
                people_posts.append(post)

    paginator = Paginator(people_posts, 3)
    page_number = request.GET.get('page')
    page_posted = paginator.get_page(page_number)

    all_likes = Like.objects.all()

    who_liked = []
    try:
        for like in all_likes:
            if like.user.id == request.user.id:
                who_liked.append(like.post.id)
    except: 
        who_liked = []

    return render(request, "network/following.html", {
        "page_posted": page_posted,
        "who_liked" : who_liked

    })

def edit (request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message" :"Chage done", "data": data["content"]})


def toggle_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like_exists = Like.objects.filter(user=user, post=post).exists()

    if like_exists:
        Like.objects.filter(user=user, post=post).delete()
        total_likes = post.post_like.count()
        return JsonResponse({"message": "Disliked!", "total_likes": total_likes, "liked": False})
    
    else:
        new_like = Like(user=user, post=post)
        new_like.save()
        total_likes = post.post_like.count()
        return JsonResponse({"message": "Liked!", "total_likes": total_likes, "liked": True})

