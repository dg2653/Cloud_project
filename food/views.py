from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from .mongoquery import MongoDbHandler
import json
import base64
import boto3
db_handler = MongoDbHandler('54.159.68.29', 'yelp_dataset')
access_token, secret_access_token = mongoquery.get_aws_credentials()
# s3.create_bucket(Bucket="app-bucket-dg2653",CreateBucketConfiguration={"LocationConstraint":"us-west-2"})

bucket_name = "app-bucket-dg2653"
def index(request):
    context = {'title': 'Home'}
    return render(request, 'index.html', context)


def recipe_detail(request):

    recipes_id = request.GET.get('recipe_id')
    # context = {'title': 'RecipeDetails', 'background': 'images/food9.jpg', 'recipes': Recipe.objects.filter(id=recipes_id)}
    context = {'title': 'RecipeDetails'}
    return render(request, 'detail.html', context)


@login_required
def restaurants(request):
    if request.method=="GET":
        cities = db_handler.get_distinct_cities()
        return render(request, 'restaurants.html', {'title': 'Restaurants', "cities":cities})
    else:
        categories = request.POST.getlist("categories",[])
        city = request.POST.get("city")
        restaurant_name = request.POST.get("restaurants")
        cities = db_handler.get_distinct_cities()
        data = db_handler.get_restaurants(restaurant_name, city, categories)
        return render(request, 'restaurants.html', {'title': 'Restaurants', 'data': data, "cities":cities})


@login_required
def recipes(request):
    if request.method == "GET":
        context = {'title': 'Recipes'}
        return render(request, 'recipes.html', context)
    elif request.method == "POST":
        title = request.POST['title']
        cooking_time = request.POST['cooking_time']
        ingredients = request.POST['ingredients']
        directions = request.POST['directions']
        file = request.POST.get('dish_photo')
        #dish_photo = request.POST['dish_photo']
        context = {'title': 'Recipes', 'message': 'Recipe Saved !'}
        obj = FoodRecipe(username=request.user.username, dish_title=title, cooking_time=cooking_time, ingredients=ingredients.replace("\n","<br/>"), directions=directions, dish_photo=file)
        obj.save()
        return render(request, 'recipes.html', context)


def upload_user_image(request):
    if request.method == "POST":
        image_base64 = request.POST.get("image_base64").split("base64,")[1]
        s3 = boto3.resource('s3')
        s3.Bucket(bucket_name).put_object(Key=request.user.username+"/profile_pic.png", Body=base64.b64decode(image_base64))
        context = {'title': 'Profile'}
        return render(request, 'profile.html', context)
    return redirect("/")



@login_required
def people(request):
    users = User.objects.all()
    return render(request, 'people.html', {'title': 'People', 'users':users})

@login_required
def view_profile(request):
    if request.user.username==request.GET.get('user_id'):
        return redirect("/profile/")
    s3Client = boto3.client('s3')
    filename = request.GET.get('user_id')+"/profile_pic.png"
    if isFileExists(filename):
        image_url = s3Client.generate_presigned_url('get_object', Params = {'Bucket': bucket_name, 'Key': filename}, ExpiresIn = 10)
    else:
        image_url = None
    context = {"title": "People", "recipes": FoodRecipe.objects.filter(username=request.GET.get('user_id')),\
               "isFriend": Friends.objects.filter(user_id2=request.GET.get('user_id')).first(),\
               "isFriendRequest": FriendRequests.objects.filter(user_id2=request.GET.get('user_id'), user_id1=request.user.username).first(),\
               "isFriendRespond": FriendRequests.objects.filter(user_id1=request.GET.get('user_id'), user_id2=request.user.username).first(),\
               "otherUser": AuthUser.objects.filter(username=request.GET.get('user_id')).first(),\
               "profile_pic": image_url}
    return render(request, 'other_user_profiles.html', context)


@login_required
def event(request):
    restaurant_id = request.GET.get("restaurant_id")
    data = db_handler.get_restaurant_info(restaurant_id, True)
    friends = Friends.objects.filter(user_id1=request.user.username)
    return render(request, 'event.html', {'title': 'Events', "friends": friends, "data":data})


def login_app(request):
    if request.method == "GET":
        redirect_url = request.GET.get("next", "")
        return render(request, 'login.html', {'redirect_url': redirect_url, 'background': 'images/food9.jpg'})
    elif request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        redirect_url = request.POST.get('redirect_url', '/')
        if redirect_url == '':
            redirect_url = '/'
        print("REDIRECT URL: " + redirect_url)
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(redirect_url)
        else:
            return render(request, 'login.html', {'username': username, 'password': password, 'background': 'images/food9.jpg', 'error_message': 'The login credentials are invalid!'})
    else:
        return redirect("/")


def register(request):
    if request.method=="GET":
        redirect_url = request.GET.get("next", "ASD")
        return render(request, 'register.html', {'redirect_url': redirect_url, 'background': 'images/food9.jpg'})
    elif request.method == "POST":
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        if len(User.objects.filter(username=email)) > 0:
            return render(request, 'register.html', {"username": email, "email": email, "first_name":first_name, "last_name":last_name,'background': 'images/construction.jpg', "error_message": "The User Name has already been taken. Please select a different User Name.", 'background': 'images/food9.jpg'})
        password = request.POST.get('password', '')
        re_password = request.POST.get('re_password', '')
        user = User.objects.create_user(username=email, password=password, email=email, first_name=first_name, last_name=last_name)
        user.save()
        return render(request, 'login.html', {'redirect_url': '', 'success_message': 'Registered Successfully!'})
    else:
        return redirect("/")


def get_all_restaurant_locations(request):
    if request.method=="POST":
        print ("HERE")
        data = db_handler.get_all_restaurants()
        print ("HERE2")
        return HttpResponse(content_type="application/json", content = json.dumps({"results": data}))


def logout_app(request):
    logout(request)
    return redirect("/")


@login_required
def profile_page(request):
    from io import BytesIO
    if request.method=="GET":
        if request.user.username:
            # file_content = BytesIO()
            # bucket.download_fileobj(request.user.username+"/profile_pic.png", file_content)
            s3Client = boto3.client('s3')
            filename = request.user.username+"/profile_pic.png"
            if isFileExists(filename):
                image_url = s3Client.generate_presigned_url('get_object', Params = {'Bucket': bucket_name, 'Key': filename}, ExpiresIn = 10)
            else:
                image_url = None
            events = Events.objects.filter(id__in=EventUsers.objects.filter(user_id=request.user.username).values_list('event_id',flat=True))
            event_info = []
            for eve in events:
                event_info.append(db_handler.get_restaurant_info(eve.restaurant_id, True)['name'])
            context = {'title': 'Profile', "full_name": request.user.first_name + " " + request.user.last_name, "profile_pic": image_url,\
                       "recipes": FoodRecipe.objects.filter(username=request.user.username),\
                       "friend_requests": FriendRequests.objects.filter(user_id2=request.user.username),\
                       "events": event_info}
            return render(request, 'profile.html', context)
        else:
            return render("/")


def restaurant_info(request):
    restaurant_id = request.GET.get('restaurant_id')
    data, reviews = db_handler.get_restaurant_info(restaurant_id)
    context = {"title": "Restaurants", "data": data[0], "days": ["Monday","Tuesday","Wednesday","Thursday","Friday", "Saturday","Sunday"], "reviews":reviews}
    return render(request, 'restaurant_info.html', context)


@login_required
def delete_recipe(request):
    recipe_id = request.GET.get("recipe_id",None)
    if recipe_id:
        FoodRecipe.objects.filter(food_recipe_id=recipe_id).delete()
    return redirect("/profile/")



@login_required
def friend_request(request):
    user_id = request.GET.get("user_id")
    req = FriendRequests(user_id2=user_id, user_id1=request.user.username)
    req.save()
    return redirect("/view_profile?user_id="+user_id)


@login_required
def add_friend(request):
    user_id = request.GET.get("user_id")
    obj = Friends(user_id1=user_id, user_id2=request.user.username)
    obj.save()
    obj = Friends(user_id2=user_id, user_id1=request.user.username)
    obj.save()
    FriendRequests.objects.filter(user_id2=request.user.username, user_id1=user_id).delete()
    return redirect("/profile/")


@login_required
def remove_friend(request):
    user_id = request.GET.get("user_id")
    FriendRequests.objects.filter(user_id2=request.user.username, user_id1=user_id).delete()
    return redirect("/profile/")


def isFileExists(filename):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    objs = list(bucket.objects.filter(Prefix=filename))
    if len(objs) > 0 and objs[0].key == filename:
        return True
    else:
        return False

@login_required
def create_event(request):
    restaurant_id = request.POST.get("restaurant_id")
    friends = Friends.objects.filter(user_id1=request.user.username)
    event = Events(creator_id=request.user.username, restaurant_id=restaurant_id)
    event.save()
    add_friend_to_event = EventUsers(event_id=event.id, user_id=request.user.username)
    add_friend_to_event.save()
    for friend in friends:
        if request.POST.get(friend.user_id2,"off")=="on":
            add_friend_to_event = EventUsers(event_id=event.id, user_id=friend.user_id2)
            add_friend_to_event.save()
    return redirect("/restaurants/")
