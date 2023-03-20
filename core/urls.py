from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('setting', views.setting, name="setting"),
    path('signin', views.signin, name="signin"),
    path('logout', views.logout, name="logout"),
    path('upload', views.upload, name="upload"),
    path('follow', views.follow, name="follow"),
    path('search', views.search, name="search"),
    path('like_post', views.like_post, name="like_post"),
    path('delete_post', views.delete_post, name="delete_post"),
    path('profile/<str:person>', views.profile, name="profile"),
]