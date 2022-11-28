from django.contrib.auth.models import AbstractUser
from django.db import models


class StudentList(models.Model):
    student_id = models.IntegerField()
    first_name = models.CharField(max_length=18)
    last_name = models.CharField(max_length=18)

    def __str__(self):
        return f"{self.last_name}{self.first_name}-{self.student_id}"


class User(AbstractUser):
    STATUS = (
        ("Student", "Student"),
        ("Teaching Assistant", "Teaching Assistant"),
        ("Teacher", "Teacher")
    )
    status = models.CharField(
        max_length=18,
        choices=STATUS,
        default="Student"
    )
    is_email_verified = models.BooleanField(default=False)


class Course(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Coursework(models.Model):
    course = models.OneToOneField(
        Course,
        on_delete=models.PROTECT,
        unique=True,
        related_name="coursework_name"
    )
    taken_person = models.ManyToManyField(
        User,
        blank=True,
        related_name="coursework_taken"
    )

    def __str__(self):
        return self.course.name


class Assignment(models.Model):
    coursework = models.ForeignKey(
        Coursework,
        on_delete=models.PROTECT,
        related_name="assignment"
    )
    title = models.CharField(max_length=128)
    created_on = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title


class AssigmentStatus(models.Model):
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.PROTECT,
        related_name="status"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assignment_student"
    )
    memo = models.TextField(
        blank=True,
        null=True
    )
    upload_file = models.FileField(null=True)
    upload_status = models.BooleanField(default=False)
