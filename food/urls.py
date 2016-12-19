from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^recipes/', views.recipes, name="recipes"),
    url(r'^restaurants/', views.restaurants, name="restaurants"),
    url(r'^people/', views.people, name="people"),
    url(r'^event/', views.event, name="event"),
    url(r'^accounts/login/', views.login_app, name="login"),
    url(r'^accounts/logout/', views.logout_app, name="logout"),
    url(r'^accounts/register/', views.register, name="register"),
    url(r'^view_recipe/', views.recipe_detail, name="details"),
    url(r'^get_all_restaurant_locations/', views.get_all_restaurant_locations, name="get_all_restaurant_locations"),
    url(r'^upload_user_image/', views.upload_user_image, name="upload_user_image"),
    url(r'^restaurant_info/', views.restaurant_info, name="restaurant_info"),
    url(r'^profile/', views.profile_page, name="my profile"),
    url(r'^view_profile', views.view_profile, name="view_profile"),
]
