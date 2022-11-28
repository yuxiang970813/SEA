from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("activate/<uidb64>/<token>", views.activate_user, name="activate_user"),
    path("coursework/create", views.create_coursework, name="create_coursework"),
    path("coursework/join", views.join_coursework, name="join_coursework")
]
