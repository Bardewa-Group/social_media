from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from .models import Profile, Post, LikePost, FollowUser
from django.contrib.auth.decorators import login_required
from itertools import chain
# Create your views here.


@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    users = User.objects.all()
    users = users[1:]
    posts = Post.objects.all()

    for post in posts:
        post_object = User.objects.get(username=post.user)
        post_user = Profile.objects.get(user=post_object)
        print(post_user.profileImg.url)
        break

    context = {
        'user_profile': user_profile,
        'posts': posts,
        "post_user": post_user,
        "users": users,
    }

    return render(request, 'index.html', context)


@login_required(login_url='signin')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get('profile') == None:
            profile = user_profile.profileImg
        else:
            profile = request.FILES.get('profile')

        bio = request.POST['bio']
        location = request.POST['location']

        # inseting the value
        user_profile.profileImg = profile
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        return redirect('index')
    return render(request, 'setting.html', {'user_data': user_profile})


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def delete_post(request):
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect('/')


@login_required(login_url='signin')
def search(request):

    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


def signin(request):

    if request.method == "POST":
        password = request.POST['password']
        username = request.POST['username']

        if username == '' or password == '':
            messages.info(request, 'Please fill every fields !')
            return redirect('signin')

        user = authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credintials invalid !')
            return redirect('signin')

    return render(request, 'signin.html')


@login_required(login_url='signin')
def profile(request, person):
    user_object = User.objects.get(username=person)
    user_profile = Profile.objects.get(user=user_object)
    user_post = Post.objects.filter(user=user_object)
    user_post_len = len(user_post)
    login_user = request.user.username

    follow_post = FollowUser.objects.filter(
        user=person, follower=login_user).first()

    if follow_post == None:
        follow = 0
    else:
        follow = 1

    follower_count = len(FollowUser.objects.filter(user=person))
    following_count = len(FollowUser.objects.filter(follower=person))

    context = {
        "user_object": user_object,
        "user_profile": user_profile,
        "user_post": user_post,
        "user_post_len": user_post_len,
        "login_user": login_user,
        "follow": follow,
        "follower_count": follower_count,
        "following_count": following_count,
    }

    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    user = request.POST['user']
    follower = request.user.username
    send_url = '/profile/' + user

    follow_post = FollowUser.objects.filter(
        user=user, follower=follower).first()

    if follow_post == None:
        new_follower = FollowUser.objects.create(user=user, follower=follower)
        new_follower.save()

    else:
        follow_post.delete()

    return redirect(send_url)


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if username == '' or email == '' or password == '' or password2 == '':
            messages.info(request, 'Please fill every fields !')
            return redirect('signup')

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken !')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken !')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                # first login then send to setting
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('setting')

        else:
            messages.info(request, 'Password do not match !')
            return redirect('signup')
    else:
        return render(request, 'signup.html')
