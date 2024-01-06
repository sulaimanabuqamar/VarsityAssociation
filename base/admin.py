from django.contrib import admin
from .models import *


class LandingPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'route_name', 'image']



admin.site.register(LandingPage, LandingPageAdmin)

