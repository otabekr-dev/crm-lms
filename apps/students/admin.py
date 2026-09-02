from django.contrib import admin
from .models import Group, Student

admin.site.register([Group, Student])