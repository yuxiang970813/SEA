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
from django.core.files import File
from django.conf import settings
from django.urls import reverse
from .models import (
    StudentList,
    User,
    Course,
    Coursework,
    Assignment,
    AssignmentStatus,
    UploadFile,
    JoinCourseworkRequest,
)
from .utils import generate_token
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
import threading
import json
import os


@login_required
def index(request):
    # Return all coursework assignments that user has joined in
    return render(
        request,
        "coursework/index.html",
        {
            "assignments": Assignment.objects.filter(
                coursework__taken_person=request.user
            )
        },
    )


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    # Send email
    def run(self):
        self.email.send()


# Reference: https://stackoverflow.com/questions/55005070/how-to-send-email-verification-link-in-django
def send_activate_email(request, user):
    # Declare email content
    email = EmailMessage(
        subject="Activate your SEA account",
        body=render_to_string(
            "coursework/activate.html",
            {
                "user": user,
                "domain": get_current_site(request),
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": generate_token.make_token(user),
            },
        ),
        from_email=settings.EMAIL_FROM_USER,
        to=[user.email],
    )
    # Send email via thread
    EmailThread(email).start()


# Reference: https://stackoverflow.com/questions/55005070/how-to-send-email-verification-link-in-django
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
        # Make email verified
        user.is_email_verified = True
        user.save()
        # Info and redirect user to login page
        messages.success(request, "Email verified, you can now login!")
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
            password=request.POST["password"],
        )
        # Invalid user
        if user is None:
            messages.error(request, "Invalid student number and/or password.")
            return HttpResponseRedirect(reverse("login"))
        # Valid user
        else:
            # Log user in if email verified
            if user.is_email_verified:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return HttpResponseRedirect(reverse("index"))
            # Email haven't verified,remind & send activate email
            else:
                send_activate_email(request, user)
                messages.info(
                    request,
                    f"Email is not verified, please check your mail box(<strong>{user.email}</strong>).",
                )
                return HttpResponseRedirect(reverse("login"))
    # User access login page
    else:
        return render(request, "coursework/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out!")
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
            messages.error(request, "Invalid student id!")
            return HttpResponseRedirect(reverse("register"))
        # Ensure password matches confirmation
        password = request.POST["password"]
        if password != request.POST["confirmation"]:
            messages.warning(request, "Passwords must match.")
            return HttpResponseRedirect(reverse("register"))
        # Try create new user
        try:
            user = User.objects.create_user(
                student_id, f"{student_id}@itd.tnnua.edu.tw", password
            )
            user.first_name = student.first_name
            user.last_name = student.last_name
            user.save()
        # Error if username already taken
        except IntegrityError:
            messages.error(request, "Student id already taken!")
            return HttpResponseRedirect(reverse("register"))
        # Redirect to login page after register successfully
        messages.success(request, "Account created successfully!")
        return HttpResponseRedirect(reverse("login"))
    # User access register page
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
                try:
                    course = Course.objects.get(pk=request.POST.get("course-id", False))
                except Course.DoesNotExist:
                    messages.error(request, "You didn't select any course!")
                    return HttpResponseRedirect(reverse("create_coursework"))
                new_coursework = Coursework.objects.create(course=course)
                new_coursework.save()
                new_coursework.taken_person.add(request.user)
                # Redirect to index after create
                messages.success(
                    request,
                    f"Coursework <strong>{new_coursework}</strong> created successfully",
                )
                return HttpResponseRedirect(
                    reverse("coursework_view", args=(new_coursework.id,))
                )
            # Remind if coursework already created
            except IntegrityError:
                messages.warning(request, "Coursework already exists!")
                return HttpResponseRedirect(reverse("create_coursework"))
        # Teacher access create coursework page
        else:
            return render(
                request,
                "coursework/create_coursework.html",
                {"courses": Course.objects.all()},
            )
    # Redirect non-teacher person to index
    else:
        messages.warning(request, "Only teacher can create coursework!")
        return HttpResponseRedirect(reverse("index"))


@login_required
def join_coursework(request):
    # User submit join coursework form
    if request.method == "POST":
        # For user later
        user = request.user
        try:
            coursework = Coursework.objects.get(pk=request.POST["coursework-id"])
        except:
            messages.warning(request, "You didn't select any coursework!")
            return HttpResponseRedirect(reverse("join_coursework"))
        taken_person = coursework.taken_person
        # Remind user if already join coursework
        if user in taken_person.all():
            messages.warning(
                request,
                f"You have already joined coursework <strong>{coursework}</strong>!",
            )
            return HttpResponseRedirect(reverse("join_coursework"))
        # User request join coursework
        else:
            # Try query for request
            try:
                JoinCourseworkRequest.objects.get(student=user, coursework=coursework)
            # User 1st time request
            except JoinCourseworkRequest.DoesNotExist:
                JoinCourseworkRequest.objects.create(
                    student=user, coursework=coursework
                ).save()
            messages.info(
                request,
                f"You have requested to join coursework <strong>{coursework}</strong>, please wait patiently for the TA to approve your request.",
            )
            return HttpResponseRedirect(reverse("index"))
    # User access join coursework page
    else:
        return render(
            request,
            "coursework/join_coursework.html",
            {"courseworks": Coursework.objects.all()},
        )


@login_required
def request_coursework(request):
    # Only TA & teacher can access this page
    if request.user.status != "Student":
        if request.method == "POST":
            # For use later
            request_coursework = JoinCourseworkRequest.objects.get(
                pk=request.POST["request-id"]
            )
            student = request_coursework.student
            student_name = (
                f"{student.last_name}{student.first_name}({student.username})"
            )
            coursework_name = request_coursework.coursework.__str__()
            # Accept request
            if request.POST["request-action"] == "Accept":
                # Add student to coursework
                request_coursework.coursework.taken_person.add(student)
                # Delete request
                request_coursework.delete()
                messages.success(
                    request,
                    f"Accept <strong>{student_name}</strong>'s request to join <strong>{coursework_name}</strong>.",
                )
            # Decline request
            else:
                request_coursework.delete()
                messages.warning(
                    request,
                    f"Decline <strong>{student_name}</strong>'s request to join <strong>{coursework_name}</strong>.",
                )
            return HttpResponseRedirect(reverse("request_coursework"))
        # User access approve request page
        else:
            return render(
                request,
                "coursework/request_coursework.html",
                {"coursework_requests": JoinCourseworkRequest.objects.all()},
            )
    # Prevent student access
    else:
        messages.warning(request, "You have not permission!")
        return HttpResponseRedirect(reverse("index"))


# API
@csrf_exempt
@login_required
def count_coursework_request(request):
    if request.method == "GET":
        return JsonResponse(
            {"request_count": int(JoinCourseworkRequest.objects.all().count())},
            status=201,
        )


@login_required
def coursework_view(request, coursework_id):
    # For user later
    coursework = Coursework.objects.get(pk=int(coursework_id))
    # Make sure user have join coursework
    if request.user in coursework.taken_person.all():
        return render(
            request, "coursework/coursework_view.html", {"coursework": coursework}
        )
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(request, "You haven't join this coursework!")
        return HttpResponseRedirect(reverse("index"))


@login_required
def create_assignment(request, coursework_id):
    # Prevent student create assignment
    if request.user.status == "Student":
        messages.error(request, "You cannot create assignment!")
        return HttpResponseRedirect(reverse("index"))
    # Only teacher & assistant can create assignment
    else:
        # User submit create assignment form
        if request.method == "POST":
            try:
                new_assignment = Assignment.objects.create(
                    coursework=Coursework.objects.get(pk=coursework_id),
                    title=request.POST["title"],
                    deadline=request.POST["datetime"],
                )
                new_assignment.save()
                messages.success(request, "Assignment created successfully!")
            except:
                messages.error(
                    request, "Failure to create assignment, please try again!"
                )
            return HttpResponseRedirect(
                reverse("coursework_view", args=(coursework_id,))
            )
        # User access create assignment page
        else:
            return render(
                request,
                "coursework/create_assignment.html",
                {"coursework": Coursework.objects.get(pk=int(coursework_id))},
            )


def user_in_coursework(user, coursework_id, assignment):
    """User & assignment must be model object."""
    # For use later
    coursework = Coursework.objects.get(pk=int(coursework_id))
    # Return boolean
    return (
        True
        if user in coursework.taken_person.all() and assignment.coursework == coursework
        else False
    )


@login_required
def submit_assignment(request, coursework_id, assignment_id):
    # For user later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure user have join coursework
    if (
        user_in_coursework(user, coursework_id, assignment)
        and not assignment.is_expired
    ):
        # Try get the assignment status
        try:
            assignment_status = AssignmentStatus.objects.get(
                assignment=assignment, student=user
            )
        # User 1st time submit
        except AssignmentStatus.DoesNotExist:
            assignment_status = AssignmentStatus.objects.create(
                assignment=assignment, student=user
            )
        # User access manage file page
        if request.method == "GET":
            return render(
                request,
                "coursework/submit_assignment.html",
                {
                    "assignment_status": assignment_status,
                    "upload_file": UploadFile.objects.filter(
                        assignment=assignment_status
                    ),
                },
            )
    # Remind & redirect to index if user haven't join coursework
    else:
        messages.error(request, "Something went wrong!")
        return HttpResponseRedirect(reverse("index"))


# API
@csrf_exempt
@login_required
def delete_file(request):
    # Delete file must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    # Get the file id from the api
    file_id = json.loads(request.body).get("file_id", "")
    # Query for request file
    try:
        file = UploadFile.objects.get(pk=int(file_id))
    except UploadFile.DoesNotExist:
        return JsonResponse({"error": "File not found."}, status=400)
    # Delete file and return message
    try:
        file.delete()
        return JsonResponse({"message": "Delete successfully!"}, status=201)
    except:
        return JsonResponse({"error": "Delete failed!"}, status=400)


# API
@csrf_exempt
@login_required
def upload_file(request):
    # Upload file must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    # Query for the assignment status
    try:
        assignment_status = AssignmentStatus.objects.get(
            assignment=Assignment.objects.get(pk=request.POST["assignmentId"]),
            student=User.objects.get(pk=request.POST["studentId"]),
        )
        # Upload file if find status
        if not assignment_status.assignment.is_expired:
            UploadFile.objects.create(
                assignment=assignment_status, file=request.FILES["file"]
            ).save()
            return JsonResponse({"message": "Upload successfully!"}, status=201)
        else:
            return JsonResponse({"error": "Assignment expired!"}, status=400)
    except AssignmentStatus.DoesNotExist:
        return JsonResponse({"error": "Something went wrong!"}, status=400)


# API
@csrf_exempt
@login_required
def edit_memo(request):
    # Edit memo must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    # Get the assignment status id from the api
    assignment_status_id = json.loads(request.body).get("assignmentStatusId", "")
    new_memo = json.loads(request.body).get("newMemo", "")
    # Query for request assignment status
    try:
        assignment_status = AssignmentStatus.objects.get(pk=int(assignment_status_id))
    except AssignmentStatus.DoesNotExist:
        return JsonResponse({"error": "Assignment status not found."}, status=400)
    # Update memo
    try:
        assignment_status.memo = new_memo
        assignment_status.save()
        return JsonResponse({"message": "Edit successfully!"}, status=201)
    except:
        return JsonResponse({"error": "Edit failed!"}, status=400)


@login_required
def view_submit_result(request, coursework_id, assignment_id):
    # For user later
    user = request.user
    assignment = Assignment.objects.get(pk=int(assignment_id))
    # Make sure request via get method & assignment is expired & user have join coursework
    if (
        request.method == "GET"
        and assignment.is_expired
        and user_in_coursework(user, coursework_id, assignment)
    ):
        # Try query assignment status
        try:
            assignment_status = AssignmentStatus.objects.get(
                assignment=assignment, student=user
            )
        # Set assignment status to None if didn't submit assignment
        except AssignmentStatus.DoesNotExist:
            assignment_status = None
        # Render page
        return render(
            request,
            "coursework/view_submit_result.html",
            {
                "assignment_status": assignment_status,
                "upload_file": UploadFile.objects.filter(assignment=assignment_status),
            },
        )
    # Showing error message & redirect to index
    else:
        messages.error(request, "Something went wrong!")
        return HttpResponseRedirect(reverse("index"))


def create_zip_file(assignment):
    # Create path and zip file name
    folder_name = (
        f"{assignment.coursework}_{assignment}_{assignment.deadline.strftime('%Y%m%d')}"
    )
    zip_file_name = f"{folder_name}.zip"
    # Compress zip file
    with ZipFile(zip_file_name, "w", compression=ZIP_DEFLATED) as zip_file:
        os.chdir(os.path.join(settings.MEDIA_ROOT, folder_name))
        for file in os.listdir():
            if file.endswith(".ptx"):
                zip_file.write(file)
    # Add that zip file to assignment
    path = Path(zip_file_name)
    os.chdir("../..")
    with path.open(mode="rb") as result_zip:
        print(path)
        print(result_zip)
        assignment.result_zip_file = File(result_zip, name=path.name)
        assignment.save()
        print(assignment.result_zip_file)
    # Delete zip file after add to assignment
    os.remove(zip_file_name)


@login_required
def assignment_result(request):
    # User must be teacher or TA & request must be post method
    if request.user.status != "Student" and request.method == "POST":
        # For use later
        assignment = Assignment.objects.get(pk=request.POST["assignment-id"])
        assignment_status = AssignmentStatus.objects.filter(assignment=assignment)
        files = UploadFile.objects.filter(assignment__in=assignment_status)
        # Create result zip file if doesn't exist
        if files and assignment.result_zip_file == "":
            create_zip_file(assignment)
        # Get the list of students who have submited the memo
        student_who_submit_memo = []
        for submitted in assignment_status:
            if submitted.memo:
                student_who_submit_memo.append(submitted.student)
        # Get the list of students who have uploaded file
        student_who_upload_file = []
        for file in files:
            student_who_upload_file.append(file.assignment.student)
        # Render page
        return render(
            request,
            "coursework/assignment_result.html",
            {
                "coursework": Coursework.objects.get(pk=request.POST["coursework-id"]),
                "assignments": assignment,
                "assignment_status": assignment_status,
                "student_who_submit_memo": student_who_submit_memo,
                "student_who_upload_file": student_who_upload_file,
            },
        )
    # Showing error message & redirect to index
    else:
        messages.error(request, "Something went wrong!")
        return HttpResponseRedirect(reverse("index"))
