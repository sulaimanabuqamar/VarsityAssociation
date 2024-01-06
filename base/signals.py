from django.db.models.signals import post_delete, post_save,pre_save
from django.dispatch import receiver
from .models import *
import os
from django.conf import settings

@receiver(pre_save, sender=LandingPage)
def delete_previous_image(sender, instance, **kwargs):
    # Check if the instance already has an ID, meaning it's an update
    if instance.id:
        try:
            # Get the existing instance from the database
            existing_instance = LandingPage.objects.get(id=instance.id)
            
            # Check if the image field has changed
            if existing_instance.image and existing_instance.image != instance.image:
                # Delete the previous image file
                if os.path.isfile(existing_instance.image.path):
                    os.remove(existing_instance.image.path)
        except LandingPage.DoesNotExist:
            pass  # Instance doesn't exist yet, nothing to delete

@receiver(post_delete, sender=LandingPage)
def delete_image_on_delete(sender, instance, **kwargs):
    # Delete the image file when the model instance is deleted
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)