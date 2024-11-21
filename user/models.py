from django.db import models
from django.utils.timezone import now


class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=False)  
    mobile_number = models.CharField(max_length=15, null=False, blank=False) 
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)  # This field must be here
    referrer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referees'
    )
    created_at = models.DateTimeField(default=now)


    def __str__(self):
        return self.email


