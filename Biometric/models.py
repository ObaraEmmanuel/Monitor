from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Employee(models.Model):

    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=8, choices=GENDER, null=True)

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username


# Hooking the following methods to the Django defined User model
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **_):
    if created:
        Employee.objects.create(user=instance)
    try:
        instance.employee.save()
    except Exception:
        pass


class Log(models.Model):
    LOG_TYPE_MAP = {
        1: "Check in",
        2: "Check out",
    }

    LOG_TYPE = tuple(zip(LOG_TYPE_MAP.keys(), LOG_TYPE_MAP.values()))

    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now())
    nature = models.IntegerField(choices=LOG_TYPE, null=False)

    def __unicode__(self):
        return f"{self.LOG_TYPE_MAP.get(self.nature)} by {self.employee.username} at {self.date.strftime('%c')}"

    def __str__(self):
        return f"{self.LOG_TYPE_MAP.get(self.nature)} by {self.employee.username} at {self.date.strftime('%c')}"
