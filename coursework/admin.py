from .models import Assignment, AssignmentStatus, Course, Coursework, JoinCourseworkRequest, StudentList, UploadFile, User
from django.contrib import admin


class UserDisplay(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "last_name",
        "first_name",
        "status",
        "is_staff",
        "is_email_verified")


class StudentListAdmin(admin.ModelAdmin):
    display = ("student_id", "last_name", "first_name")
    list_display = display
    search_fields = display


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "coursework", "created_on", "deadline")


class AssignmentStatusAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "memo")


class JoinCourseworkRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "coursework")


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentStatus, AssignmentStatusAdmin)
admin.site.register(Course)
admin.site.register(Coursework)
admin.site.register(JoinCourseworkRequest, JoinCourseworkRequestAdmin)
admin.site.register(StudentList, StudentListAdmin)
admin.site.register(UploadFile)
admin.site.register(User, UserDisplay)
