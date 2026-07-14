from django.contrib import admin
from .models import Course, Category, CourseMaterial, EnrolledStudent, PaymentRecord

# Register your models here.
admin.site.register([
    Category,
    Course, CourseMaterial,
    EnrolledStudent, PaymentRecord
])