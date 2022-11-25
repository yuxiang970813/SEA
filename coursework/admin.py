from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import StudentList, User


class UserDisplay(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "last_name",
        "first_name",
        "status",
        "is_staff",
        "is_email_verified"
    )


class StudentListAdmin(admin.ModelAdmin):
    display = (
        "student_id",
        "last_name",
        "first_name"
    )
    list_display = display
    search_fields = display


admin.site.register(StudentList, StudentListAdmin)
admin.site.register(User, UserDisplay)
