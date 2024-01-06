from django.db import models


class LandingPage(models.Model):
    image = models.ImageField(
        upload_to='images/', blank=True, null=True)
    title = models.CharField(
        max_length=225)
    route_name = models.CharField(
        max_length=225, default='home', help_text="this route name given url.py. Leave default home if  no route yet given.E.g for basketball the route name is schedule")

