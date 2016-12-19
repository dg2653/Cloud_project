from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from .mongoquery import MongoDbHandler
import json
db_handler = MongoDbHandler('localhost','yelp_dataset')



def index(request):
    if request.method == "POST":
        print(request.POST)
        return HttpResponse()
    context = {'title': 'Home', 'background': 'images/food9.jpg', "full_name": request.user.first_name + " "+request.user.last_name}
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
def people(request):
    return render(request, 'index.html', {'title': 'People'})


@login_required
def event(request):
    return render(request, 'event.html', {'title': 'Events'})

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
        #file = request.POST.get('dish_photo')
        #dish_photo = request.POST['dish_photo']

        context = {'title': 'Recipes', 'message': 'Recipe Saved !'}
        return render(request, 'recipes.html', context)


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
    if request.method=="GET":
        username = request.GET.get("username")
        if request.user.username == username:
            return redirect("/")
        user_obj = User.objects.filter(username=username)
        if len(user_obj)==0:
            return
        return HttpResponse()


def upload_user_image(request):
    if request.method=="POST":
        image = request.POST.get("image_base64")
        if image!="":
            image = image.split("base64,")[1]
            obj = UserProfile.objects.filter(username=request.user.username)
            print("OBJECT: "+str(obj))
            if len(obj)==0:
                obj = UserProfile(username = request.user.username, profile_pic=image)
                obj.save()
            else:
                obj[0].update(profile_pic=image)
        return HttpResponse()


def get_user_image(request):
    if request.method=="POST":
        profile_pic = UserProfile.objects.filter(username=request.user.username).first()
        if not profile_pic:
            profile_pic = ''
        else:
            profile_pic = profile_pic.profile_pic
            # profile_pic = ''
        return HttpResponse(status=200, content_type="application/json", content=json.dumps({"result":profile_pic}))


def restaurant_info(request):
    restaurant_id = request.GET.get('restaurant_id')
    data, reviews = db_handler.get_restaurant_info(restaurant_id)
    context = {"title": "Restaurants", "data": data[0], "days":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "reviews":reviews}
    return render(request, 'restaurant_info.html', context)
