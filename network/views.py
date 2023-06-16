from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import redirect

import json

from .models import *


def index(request):
    #all_posts = Post.objects.all().order_by('-date_created')
    #all post from that user
    all_posts = Post.objects.filter(creater=request.user)

    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]
        communitys = Community.objects.filter(userlist=request.user)
        #post from community user inside only
        for community in communitys:
            print(Post.objects.filter(community=community.community_id))
            all_posts = all_posts.union(Post.objects.filter(community=community.community_id))
    all_posts = all_posts.order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "communitys": communitys,
        "page": "all_posts",
        'profile': False
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
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(
            f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(
            f"--------------------------Cover: {cover}----------------------------")

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
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("quizz"))
    else:
        return render(request, "network/register.html")


def quizz(request):
    radioQuestions = [
        {
            "number": 1,
            "question": "I have a kind word for everyone",
            "options": ["1", "2", "3"],
        },
        {
            "number": 2,
            "question": "I am always prepared",
            "options": ["1", "2", "3"],
        },
        {
            "number": 3,
            "question": "I feel comfortable around people",
            "options": ["1", "2", "3"],
        },
        {
            "number": 4,
            "question": "I often feel blue",
            "options": ["1", "2", "3"],
        },
        {
            "number": 5,
            "question": "I am very good at identifying the emotions I am feeling",
            "options": ["1", "2", "3"],
        },
        {
            "number": 6,
            "question": "I believe in the importance of art",
            "options": ["1", "2", "3"],
        },
        {
            "number": 7,
            "question": "I am the life of the party",
            "options": ["1", "2", "3"],
        },
        {
            "number": 8,
            "question": "I am very good at reading body language",
            "options": ["1", "2", "3"],
        },
        {
            "number": 9,
            "question": "There are many things that I do not like about myself",
            "options": ["1", "2", "3"],
        },
        {
            "number": 10,
            "question": "My moods change easily",
            "options": ["1", "2", "3"],
        }
    ]

    if request.method == "GET":

        return render(request, "network/quizz.html", {
            "radioQuestions": radioQuestions,
        })

    if request.method == "POST":
        # print(request.POST)
        return JsonResponse({"message": "POST request received.", "data": request.POST}, status=200)


def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
        communitys = Community.objects.filter(userlist=request.user)

    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count,
        "communitys": communitys,

    })


def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(
            followers=request.user).values('user')
        all_posts = Post.objects.filter(
            creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]
        communitys = Community.objects.filter(userlist=request.user)
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following",
            "communitys": communitys,
        })
    else:
        return HttpResponseRedirect(reverse('login'))


def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(
            savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]
        communitys = Community.objects.filter(userlist=request.user)
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved",
            "communitys": communitys,
        })
    else:
        return HttpResponseRedirect(reverse('login'))


@login_required
def create_post(request):
    if request.method == 'POST':
        prevurl = request.META.get('HTTP_REFERER')
        communityid = -1 
        if ("/community/" in prevurl):
            communityid = prevurl.split('/community/')[1]
        print(communityid)
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        try:
            if (communityid != -1):
                post = Post.objects.create(creater=request.user, content_text=text, content_image=pic, community=Community.objects.get(community_id=communityid))
            else:
                post = Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")


@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()

            if (post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if (post.content_image):
                post_image = post.img_url()
            else:
                post_image = False

            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
        return HttpResponse("Method must be 'POST'")


@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))

@login_required
@csrf_exempt
def choose_group(request):
    if request.user.is_authenticated:
        communitys = Community.objects.all()
    return render(request, 'network/choosegroup.html', {
        "communitys": communitys,
    })


@login_required
@csrf_exempt
def join_community(request, id):
    if request.user.is_authenticated:
            community = Community.objects.get(community_id=id)
            print(community)
            try:
                community.userlist.add(request.user)
                community.save()
                #return HttpResponseRedirect(request.path_info)
                url = reverse('community', kwargs={'id': id})
                return HttpResponseRedirect(url)
            except Exception as e:
                return HttpResponse(e)
    else:
        return HttpResponseRedirect(reverse('login'))

@login_required
@csrf_exempt
def leave_community(request, id):
    if request.user.is_authenticated:
            community = Community.objects.get(community_id=id)
            print(community)
            try:
                community.userlist.remove(request.user)
                community.save()
                #return HttpResponseRedirect(request.path_info)
                url = reverse('community', kwargs={'id': id})
                return HttpResponseRedirect(url)
            except Exception as e:
                return HttpResponse(e)
    else:
        return HttpResponseRedirect(reverse('login'))


@login_required
@csrf_exempt 
def community(request, id):
    if request.user.is_authenticated:
        community = Community.objects.get(community_id=id)
        communitys = Community.objects.filter(userlist=request.user)
        posts = Post.objects.filter(community=community).order_by('-date_created')
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]
        return render(request, "network/groupview.html", {
            "user": request.user,
            "posts": posts,
            "suggestions": suggestions,
            "page": "group",
            "community": community,
            "communitys": communitys,
        })
    else:
        return HttpResponseRedirect(reverse('login'))


@login_required
@csrf_exempt
def joingroup(request, groupid):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            group = Community.objects.get(pk=groupid)
            print(group)
            try:
                group.userlist.add(request.user)
                group.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(
                f".....................Follower: {request.user}......................")
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(
                f".....................Unfollower: {request.user}......................")
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(
                    post=post, commenter=request.user, comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)

        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))
