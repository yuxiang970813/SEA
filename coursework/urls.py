from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("activate/<uidb64>/<token>", views.activate_user, name="activate_user"),
    path("coursework/create", views.create_coursework, name="create_coursework"),
    path("coursework/join", views.join_coursework, name="join_coursework"),
    path("coursework/<int:coursework_id>",
         views.coursework_view, name="coursework_view"),
    path("coursework/<int:coursework_id>/assignment/create",
         views.create_assignment, name="create_assignment"),
    path("coursework/<int:coursework_id>/assignment/<int:assignment_id>",
         views.assignment_view, name="assignment_view"),
    path("coursework/<int:coursework_id>/assignment/<int:assignment_id>/edit",
         views.edit_memo, name="edit_memo")
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
