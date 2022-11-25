from django.utils.encoding import force_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse

from .models import StudentList, User
from .utils import generate_token
import threading


@login_required
def index(request):
    return render(request, "coursework/index.html")


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_activate_email(request, user):
    email = EmailMessage(
        subject="Activate your SEA account",
        body=render_to_string("coursework/activate.html", {
            "user": user,
            "domain": get_current_site(request),
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": generate_token.make_token(user)
        }),
        from_email=settings.EMAIL_FROM_USER,
        to=[user.email]
    )
    EmailThread(email).start()


def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(
            request,
            "Email verified, you can now login"
        )
        return HttpResponseRedirect(reverse(
            "login"
        ))
    else:
        return HttpResponse(
            "Something went wrong, please contact teaching assistant."
        )


def login_view(request):
    # Prevent login again
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(
            "index"
        ))
    # User submit login form
    if request.method == "POST":
        # Try authenticate user
        user = authenticate(
            request,
            username=request.POST["student-id"],
            password=request.POST["password"]
        )
        # Invalid user
        if user is None:
            messages.error(
                request,
                "Invalid student number and/or password."
            )
            return HttpResponseRedirect(reverse(
                "login"
            ))
        # Valid user
        else:
            # Log user in if email verified
            if user.is_email_verified:
                login(request, user)
                messages.success(
                    request,
                    "Logged in successfully!"
                )
                return HttpResponseRedirect(reverse(
                    "index"
                ))
            # Email haven't verified,remind & send activate email
            else:
                send_activate_email(request, user)
                messages.info(
                    request,
                    "Email is not verified, please check your mail box."
                )
                return HttpResponseRedirect(reverse(
                    "login"
                ))
    # User visit login page
    else:
        return render(request, "coursework/login.html")


def logout_view(request):
    logout(request)
    messages.success(
        request,
        "Logged out successfully!"
    )
    return HttpResponseRedirect(reverse(
        "login"
    ))


def register(request):
    # Prevent resigter when logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse(
            "index"
        ))
    # User submit register form
    if request.method == "POST":
        # Student id validation
        student_id = request.POST["student-id"]
        try:
            student = StudentList.objects.get(
                student_id=student_id
            )
        except StudentList.DoesNotExist:
            messages.error(
                request,
                "Invalid student id!"
            )
            return HttpResponseRedirect(reverse(
                "register"
            ))
        # Ensure password matches confirmation
        password = request.POST["password"]
        if password != request.POST["confirmation"]:
            messages.warning(
                request,
                "Passwords must match."
            )
            return HttpResponseRedirect(reverse(
                "register"
            ))
        # Try create new user
        try:
            user = User.objects.create_user(
                student_id,
                f"{student_id}@itd.tnnua.edu.tw",
                password
            )
            user.first_name = student.first_name
            user.last_name = student.last_name
            user.save()
        # Error if username already taken
        except IntegrityError:
            messages.error(
                request,
                "Student id already taken!"
            )
            return HttpResponseRedirect(reverse(
                "login"
            ))
        # Redirect to login page after register successfully
        messages.success(
            request,
            "Account created successfully!"
        )
        return HttpResponseRedirect(reverse(
            "login"
        ))
    # User visit register page
    else:
        return render(request, "coursework/register.html")
