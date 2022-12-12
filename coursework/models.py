from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
import os


class StudentList(models.Model):
    student_id = models.IntegerField()
    first_name = models.CharField(max_length=18)
    last_name = models.CharField(max_length=18)

    def __str__(self):
        return f"{self.last_name}{self.first_name}-{self.student_id}"

    class Meta:
        ordering = ["student_id"]


class User(AbstractUser):
    STATUS = (
        ("Student", "Student"),
        ("Teaching Assistant", "Teaching Assistant"),
        ("Teacher", "Teacher"),
    )
    status = models.CharField(max_length=18, choices=STATUS, default="Student")
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["username"]


class Course(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Coursework(models.Model):
    course = models.OneToOneField(
        Course, on_delete=models.PROTECT, unique=True, related_name="coursework_name"
    )
    taken_person = models.ManyToManyField(
        User, blank=True, related_name="coursework_taken"
    )

    def __str__(self):
        return self.course.name

    class Meta:
        ordering = ["course"]


class JoinCourseworkRequest(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="request_student"
    )
    coursework = models.ForeignKey(
        Coursework, on_delete=models.CASCADE, related_name="request_coursework"
    )

    def __str__(self):
        return f"{self.student} request join {self.coursework}."

    class Meta:
        ordering = ["student", "coursework"]


class Assignment(models.Model):
    coursework = models.ForeignKey(
        Coursework, on_delete=models.PROTECT, related_name="assignment"
    )
    title = models.CharField(max_length=128)
    created_on = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    result_zip_file = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

    @property
    def remain_time(self):
        return self.deadline - timezone.now()

    class Meta:
        ordering = ["coursework", "-created_on"]


class AssignmentStatus(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.PROTECT, related_name="status"
    )
    student = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="assignment_student"
    )
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student} upload {self.assignment}"

    class Meta:
        ordering = ["assignment", "student__username"]


def path_and_rename(instance, filename):
    # For use later
    assign = instance.assignment
    # Return path and name
    return os.path.join(
        f"{assign.assignment.coursework}_{assign.assignment}_{assign.assignment.deadline.strftime('%Y%m%d')}",
        f"{assign.student.username}.{filename.split('.')[-1]}",
    )


class UploadFile(models.Model):
    assignment = models.ForeignKey(
        AssignmentStatus, on_delete=models.CASCADE, related_name="upload_file"
    )
    file = models.FileField(blank=True, null=True, upload_to=path_and_rename)

    def __str__(self):
        return f"{self.assignment}({self.file})"

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["assignment", "assignment__student", "file"]
