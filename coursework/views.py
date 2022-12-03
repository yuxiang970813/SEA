from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_str, force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse

from .models import StudentList, User, Course, Coursework, Assignment, AssignmentStatus, UploadFile
from .utils import generate_token

import threading
import json


@login_required
def index(request):
    return render(request, "coursework/index.html", {
        "assignments": Assignment.objects.filter(coursework__taken_person=request.user)
    })


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    # Send email
    def run(self): self.email.send()


def send_activate_email(request, user):
    # Declare email content
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
    # Send email via thread
    EmailThread(email).start()


def activate_user(request, uidb64, token):
    # Try decode user
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    # Make non-user if decode fail
    except Exception:
        user = None
    # User exist & token match
    if user and generate_token.check_token(user, token):
        # Make email verified, info and redirect user to login page
        user.is_email_verified = True
        user.save()
        messages.success(
            request, "Email verified, you can now login"
        )
        return HttpResponseRedirect(reverse("login"))
    # User doesn't exist or token doen't match
    else:
        return HttpResponse("Something went wrong, please contact teaching assistant.")


def login_view(request):
    # Prevent login again
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
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
                request, "Invalid student number and/or password."
            )
            return HttpResponseRedirect(reverse("login"))
        # Valid user
        else:
            # Log user in if email verified
            if user.is_email_verified:
                login(request, user)
                messages.success(
                    request, "Logged in successfully!"
                )
                return HttpResponseRedirect(reverse("index"))
            # Email haven't verified,remind & send activate email
            else:
                send_activate_email(request, user)
                messages.info(
                    request, "Email is not verified, please check your mail box."
                )
                return HttpResponseRedirect(reverse("login"))
    # User visit login page
    else:
        return render(request, "coursework/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(
        request, "Logged out successfully!"
    )
    return HttpResponseRedirect(reverse("login"))


def register(request):
    # Prevent resigter when logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    # User submit register form
    if request.method == "POST":
        # Student id validation
        student_id = request.POST["student-id"]
        try:
            student = StudentList.objects.get(student_id=student_id)
        except StudentList.DoesNotExist:
            messages.error(
                request, "Invalid student id!"
            )
            return HttpResponseRedirect(reverse("register"))
        # Ensure password matches confirmation
        password = request.POST["password"]
        if password != request.POST["confirmation"]:
            messages.warning(
                request, "Passwords must match."
            )
            return HttpResponseRedirect(reverse("register"))
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
                request, "Student id already taken!"
            )
            return HttpResponseRedirect(reverse("register"))
        # Redirect to login page after register successfully
        messages.success(
            request, "Account created successfully!"
        )
        return HttpResponseRedirect(reverse("login"))
    # User visit register page
    else:
        return render(request, "coursework/register.html")


@login_required
def create_coursework(request):
    # Only teacher can create coursework
    if request.user.status == "Teacher":
        # Teacher submit create coursework form
        if request.method == "POST":
            # Try create new coursework & add teacher to that coursework
            try:
                new_coursework = Coursework.objects.create(
                    course=Course.objects.get(pk=request.POST["course-id"])
                )
                new_coursework.save()
                new_coursework.taken_person.add(request.user)
                # Redirect to index after create
                messages.success(
                    request, "Coursework created successfully"
                )
                return HttpResponseRedirect(reverse(
                    "coursework_view",
                    args=(new_coursework.id,)
                ))
            # Remind if coursework already created
            except IntegrityError:
                messages.warning(
                    request, "Coursework already exists!"
                )
                return HttpResponseRedirect(reverse("create_coursework"))
        # Teacher visit create coursework page
        else:
            return render(request, "coursework/create_coursework.html", {
                "courses": Course.objects.all()
            })
    # Redirect non-teacher person to index
    else:
        messages.error(
            request, "Only teacher can create coursework"
        )
        return HttpResponseRedirect(reverse("index"))


@login_required
def join_coursework(request):
    # User submit join coursework form
    if request.method == "POST":
        # For user later
        user = request.user
        coursework = Coursework.objects.get(
            pk=request.POST["coursework-id"]
        )
        taken_person = coursework.taken_person
        # Remind user if already join coursework
        if user in taken_person.all():
            messages.warning(
                request, "Already joined coursework!"
            )
            return HttpResponseRedirect(reverse("join_coursework"))
        # Join user to coursework
        else:
            taken_person.add(user)
            messages.success(
                request, "Join coursework successfully"
            )
            return HttpResponseRedirect(reverse(
                "coursework_view",
                args=(coursework.id,)
            ))
    # User visit join coursework page
    else:
        return render(request, "coursework/join_coursework.html", {
            "courseworks": Coursework.objects.all()
        })


@login_required
def coursework_view(request, coursework_id):
    # For user later
    coursework = Coursework.objects.get(pk=int(coursework_id))
    # Make sure user have join coursework
    if request.user in coursework.taken_person.all():
        return render(request, "coursework/coursework_view.html", {
            "coursework": coursework
        })
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(
            request, "You haven't join this coursework!"
        )
        return HttpResponseRedirect(reverse("index"))


@login_required
def create_assignment(request, coursework_id):
    # Prevent student create assignment
    if request.user.status == "Student":
        messages.error(
            request, "You cannot create assignment!"
        )
        return HttpResponseRedirect(reverse("index"))
    # Only teacher & assistant can create assignment
    else:
        # User submit create assignment form
        if request.method == "POST":
            try:
                new_assignment = Assignment.objects.create(
                    coursework=Coursework.objects.get(pk=coursework_id),
                    title=request.POST["title"],
                    deadline=request.POST["datetime"]
                )
                new_assignment.save()
                messages.success(
                    request, "Assignment created successfully!"
                )
            except:
                messages.error(
                    request, "Failure to create assignment, please try again!"
                )
            return HttpResponseRedirect(reverse(
                "coursework_view",
                args=(coursework_id,)
            ))
        # User visit create assignment page
        else:
            return render(request, "coursework/create_assignment.html", {
                "coursework": Coursework.objects.get(pk=int(coursework_id))
            })


def user_in_coursework(user, coursework_id, assignment):
    """user & assignment must be model object"""
    # For use later
    coursework = Coursework.objects.get(pk=int(coursework_id))
    if user in coursework.taken_person.all() and assignment.coursework == coursework:
        return True
    else:
        return False


@login_required
def assignment_view(request, coursework_id, assignment_id):
    # For use later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure user have join coursework
    if user_in_coursework(user, coursework_id, assignment):
        # User submit assignment form
        if request.method == "POST":
            # Create upload assignment status
            upload_assignment = AssignmentStatus.objects.create(
                assignment=assignment,
                student=user,
                memo=request.POST["memo"]
            )
            upload_assignment.save()
            # Upload file
            files = request.FILES.getlist("upload-file")
            for file in files:
                UploadFile.objects.create(
                    assignment=upload_assignment,
                    file=file
                ).save()
                # Info user and redirect to index
            messages.success(
                request, "Assignment upload successfully!"
            )
            return HttpResponseRedirect(reverse("index"))
        # User visit submit assignment page
        else:
            return render(request, "coursework/assignment_view.html", {
                "assignment": assignment
            })
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(
            request, "Something went wrong!"
        )
        return HttpResponseRedirect(reverse("index"))


@login_required
def edit_memo(request, coursework_id, assignment_id):
    # For user later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure user have join coursework
    if user_in_coursework(user, coursework_id, assignment):
        # For user later
        assignment_status = AssignmentStatus.objects.get(
            assignment=assignment,
            student=user
        )
        # User submit edit assignment form
        if request.method == "POST":
            # Update new version memo & redirect to index
            assignment_status.memo = request.POST["memo"]
            assignment_status.save()
            messages.success(
                request, "Memo edit successfully!"
            )
            return HttpResponseRedirect(reverse("index"))
        # User visit edit assignment page
        else:
            return render(request, "coursework/edit_assignment.html", {
                "assignment_status": assignment_status
            })
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(
            request, "Something went wrong!"
        )
        return HttpResponseRedirect(reverse("index"))


@login_required
def manage_file(request, coursework_id, assignment_id):
    # For user later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure user have join coursework
    if user_in_coursework(user, coursework_id, assignment):
        # For user later
        assignment_status = AssignmentStatus.objects.get(
            assignment=assignment,
            student=user
        )
        # User visit manage file page
        if request.method == "GET":
            return render(request, "coursework/manage_file.html", {
                "assignment_status": assignment_status,
                "upload_file": UploadFile.objects.filter(assignment=assignment_status)
            })
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(
            request, "Something went wrong!"
        )
        return HttpResponseRedirect(reverse("index"))


@csrf_exempt
@login_required
def delete_file(request):
    # Delete file must be via POST
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required."},
            status=400
        )
    # Get the file id from the api
    file_id = json.loads(request.body).get("file_id", "")
    # Query for request file
    try:
        file = UploadFile.objects.get(pk=int(file_id))
    except UploadFile.DoesNotExist:
        return JsonResponse(
            {"error": "File not found"},
            status=400
        )
    # Delete file and return message
    try:
        file.delete()
        return JsonResponse(
            {"message": "Delete successfully!"},
            status=200
        )
    except:
        return JsonResponse(
            {"error": "Delete failed!"},
            status=400
        )


@login_required
def upload_file(request, coursework_id, assignment_id):
    # For user later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure user have join coursework
    if user_in_coursework(user, coursework_id, assignment):
        # User upload file
        if request.method == "POST":
            assignment_status = AssignmentStatus.objects.get(
                assignment=assignment,
                student=user
            )
            # Upload file
            UploadFile.objects.create(
                assignment=assignment_status,
                file=request.FILES["file-for-upload"]
            ).save()
            messages.success(
                request, "Upload successfully"
            )
            return HttpResponseRedirect(reverse(
                "manage_file",
                args=(
                    coursework_id,
                    assignment_id
                )
            ))
        # Upload must be post request!
        else:
            messages.error(
                request, "POST request required!"
            )
            return HttpResponseRedirect(reverse("index"))
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(
            request, "Something went wrong!"
        )
        return HttpResponseRedirect(reverse("index"))


@login_required
def assignment_result(request):
    # Student can't visit result page
    if request.user.status == "Student":
        messages.warning(
            request, "You have not permission!"
        )
        return HttpResponseRedirect(reverse("index"))
    # Teacher or teaching assistant visit result page
    else:
        if request.method == "GET":
            return render(request, "coursework/assignment_result.html", {
                # TODO
            })
