from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import redirect
import openai
import json
import requests
from django.middleware.csrf import get_token

from .models import *
messages = []
system_msg = "You are a psychologist. Your task is to chat with users. Maximum 5 answers. If the conversation get too long, tell them you can help they reach to master users or professionals"
messages.append({"role": "system", "content": system_msg})
openai.api_key = "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"


def index(request):
    all_posts = Post.objects.none()
    communitys = Community.objects.none()

    followings = []
    suggestions = []

    if request.user.is_authenticated:
        all_posts = all_posts.union(Post.objects.filter(creater=request.user))
        followings = Follower.objects.filter(
            followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(
            username=request.user.username).order_by("?")[:6]
        communitys = Community.objects.filter(userlist=request.user)
        # post from community user inside only
        for community in communitys:
            all_posts = all_posts.union(
                Post.objects.filter(community=community.community_id))

    all_posts = all_posts.order_by('-date_created')
    all_post = all_posts.reverse()
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)

    callRedFlag = 0
    if request.user.is_authenticated:
        if (request.user.redflag >= 5 and request.user.redflag % 5 == 0):
            callRedFlag = 1
        elif (request.user.redflag <= -5 and request.user.redflag % 5 == 0):
            callRedFlag = -1
    print(
        f"--------------------------Redflag: {callRedFlag}----------------------------")
    # Return the call red flag with index.html, callredflag = -1 if negative and 1 if positive or else is neutral
    # Use if block in the index to call the script
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "communitys": communitys,
        "page": "all_posts",
        'profile': False,
        'redflag': callRedFlag
    })


@csrf_exempt
def chatapi(request, msg):
    response = JsonResponse("Not authenticated", safe=False)
    print(
        f"--------------------------Message: {request.user.is_authenticated} ----------------------------")
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        if (user.messageAmountwithBot >= 5):
            # If the user chat with the bot more than 10 times, the bot will stop chatting with the user
            reply = "Deeply apologize but I can't understand much human emotions. You can try connect to other users who spread positive energy or professionals like our psychologists"
            msg1 = "This is an active user in our community. You can try to connect with them"
            img_msg1 = "https://scontent.fhan14-4.fna.fbcdn.net/v/t1.15752-9/355106013_533212115538234_3178483906043113328_n.png?_nc_cat=109&ccb=1-7&_nc_sid=ae9488&_nc_ohc=tlLHsBlH7S0AX-Wa5UP&_nc_ht=scontent.fhan14-4.fna&oh=03_AdSB3AuFhlj4bCGvoZu-2_2xN70eK6kPUuRz_wznh17JHA&oe=64B54ABE"

            msg2 = "This is one of our professional psychologists. You can try to connect with them"
            img_msg2 = "https://c8.alamy.com/comp/2BNJ26T/medical-nurses-and-doctors-avatars-in-cartoon-style-2BNJ26T.jpg"

            msg3 = "This a a small quiz you can use to find out about your potential mental problems"
            link_quizz = "http://127.0.0.1:8000/n/quizz_mental"

            response = JsonResponse({"reply": reply, "msg1": msg1, "img_msg1": img_msg1, "msg2": msg2,
                                    "img_msg2": img_msg2, "msg3": msg3, "link_quizz": link_quizz}, safe=False)

        else:
            user.messageAmountwithBot += 1
            user.save()
            message = msg
            # input cua user
            messages.append({"role": "user", "content": message})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages)
            # reply of chatgpt
            reply = response["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": reply})
            msg1 = ""
            img_msg1 = ""
            msg2 = ""
            img_msg2 = ""
            response = JsonResponse(
                {"reply": reply, "msg1": msg1, "img_msg1": img_msg1, "msg2": msg2, "img_msg2": img_msg2}, safe=False)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


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
            "question": "I accept people the way they are",
            "options": ["1", "2", "3"],
        },
        {
            "number": 2,
            "question": "I am very good at reading body language",
            "options": ["1", "2", "3"],
        },
        {
            "number": 3,
            "question": "I describe my emotional experiences vividly",
            "options": ["1", "2", "3"],
        },
        {
            "number": 4,
            "question": "I am often troubled by negative thoughts",
            "options": ["1", "2", "3"],
        },
        {
            "number": 5,
            "question": "My moods change easily",
            "options": ["1", "2", "3"],
        },
        {
            "number": 6,
            "question": "I treat everyone with kindness and sympathy",
            "options": ["1", "2", "3"],
        },
        {
            "number": 7,
            "question": "I am skilled in handling social situations",
            "options": ["1", "2", "3"],
        },
        {
            "number": 8,
            "question": "I often feel anxious about what could go wrong",
            "options": ["1", "2", "3"],
        },
        {
            "number": 9,
            "question": "I consider myself to be charming",
            "options": ["1", "2", "3"],
        },
        {
            "number": 10,
            "question": "I often worry that I am not good enough",
            "options": ["1", "2", "3"],
        },
        {
            "number": 11,
            "question": "I stop what I am doing to help other people",
            "options": ["1", "2", "3"],
        },
        {
            "number": 12,
            "question": "I often think about why I am feeling the way I am feeling",
            "options": ["1", "2", "3"],
        },
        {
            "number": 13,
            "question": "I change my plans frequently",
            "options": ["1", "2", "3"],
        },
        {
            "number": 14,
            "question": "I take care of other people before taking care of myself",
            "options": ["1", "2", "3"],
        },
        {
            "number": 15,
            "question": "I am very good at helping people work through their emotions",
            "options": ["1", "2", "3"],
        }
    ]

    if request.method == "GET":

        return render(request, "network/quizz.html", {
            "radioQuestions": radioQuestions,
        })

    if request.method == "POST":
        user_answer = request.POST
        request.session['user_answer'] = user_answer
        return HttpResponseRedirect(reverse("AI_models:personality_detect"))

# quizz for mentals


def quizz_mental(request):
    mentalQuestions = [
        {
            "number": 1,
            "question": "I have recurring thoughts or images about the event",
            "options": ["1", "2", "3"],
        },
        {
            "number": 2,
            "question": "I frequently struggle with organizing tasks or maintaining a routine",
            "options": ["1", "2", "3"],
        },
        {
            "number": 3,
            "question": "I find myself impulsively interrupting others or speaking without thinking",
            "options": ["1", "2", "3"],
        },
        {
            "number": 4,
            "question": "I had recurring thoughts of death or suicide and I made any suicide attempts",
            "options": ["1", "2", "3"],
        },
        {
            "number": 5,
            "question": "I have difficulty organizing tasks and activities",
            "options": ["1", "2", "3"],
        },
        {
            "number": 6,
            "question": "I prefer to have a specific routine or dislike sudden changes in plans",
            "options": ["1", "2", "3"],
        },
        {
            "number": 7,
            "question": "I often struggle with initiating or maintaining conversations with others",
            "options": ["1", "2", "3"],
        },
        {
            "number": 8,
            "question": "I have trouble sleeping or sleeping too much",
            "options": ["1", "2", "3"],
        },
        {
            "number": 9,
            "question": "I have a restricted range of interests and activities",
            "options": ["1", "2", "3"],
        },
        {
            "number": 10,
            "question": "I have trouble concentrating or making decisions",
            "options": ["1", "2", "3"],
        },
        {
            "number": 11,
            "question": "I experience intrusive and unwanted thoughts, images, or urges",
            "options": ["1", "2", "3"],
        },
        {
            "number": 12,
            "question": "I find myself engaging in repetitive behaviors or rituals to alleviate anxiety or distress",
            "options": ["1", "2", "3"],
        },
        {
            "number": 13,
            "question": "I felt compelled to follow strict and specific rules or patterns in my daily life",
            "options": ["1", "2", "3"],
        },
        {
            "number": 14,
            "question": "I experienced or witnessed a traumatic event that continues to affect you emotionally",
            "options": ["1", "2", "3"],
        },
        {
            "number": 15,
            "question": "I often avoid situations, places, or activities that remind you of the trauma",
            "options": ["1", "2", "3"],
        }
    ]

    if request.method == "GET":

        return render(request, "network/quizz_mental.html", {
            "mentalQuestions": mentalQuestions,
        })

    if request.method == "POST":
        print('xxxxxxxxxxxxxxxx')
        mental_answer = request.POST
        print(mental_answer)
        request.session['mental_answer'] = mental_answer
        return HttpResponseRedirect(reverse("AI_models:mental_detect"))


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

        print("*"*20)
        print(communityid)
        text = request.POST.get('text')
        pic = request.FILES.get('picture')

        # Get user_name
        user = request.user
        user_name = user.username
        userObject = User.objects.get(username=user_name)

        # Call sentiment analysis API
        response = requests.post(
            'http://127.0.0.1:8000/AI_models/sentiment_analysis/', data={'content_text': text})
        if response.status_code == 200:  # Success get to the API from the Sentiment Analysis Model
            result = response.json().get('result')
            changeValue = 0
            if (result[0] > 0.9):
                changeValue -= 1
            if (result[2] > 0.9):
                changeValue += 1

            post = Post(creater=request.user,
                        content_text=text, content_image=pic)

            # If the post is created in a community, update post as community
            if (communityid != -1):
                post.community_id = communityid

            post.save()

            userObject.redflag += changeValue
            userObject.save()

            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponse('Failed to get a valid response from the AI model.')
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
            # return HttpResponseRedirect(request.path_info)
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
            # return HttpResponseRedirect(request.path_info)
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
        posts = Post.objects.filter(
            community=community).order_by('-date_created')
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
