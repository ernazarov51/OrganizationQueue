from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    pass
    # class RoleChoices(models.TextChoices):
    #     employee='employee','Employee'
    #     user='user','User'
    #     admin='admin','Admin'
    #
    # role=models.CharField(max_length=10,choices=RoleChoices.choices,default=RoleChoices.user)
    # organization=models.ForeignKey('core.Organization',on_delete=models.SET_NULL,related_name='employees',null=True,blank=True)

class Employee(models.Model):
    username=models.CharField(unique=True,max_length=255)
    date=models.DateTimeField(auto_now_add=True)
    organization=models.ForeignKey('core.Organization',models.CASCADE,related_name='employees')


class Organization(models.Model):
    owner=models.ForeignKey('core.User',models.CASCADE,related_name='organizations')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    is_accepted=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    organization=models.ForeignKey('core.Organization',models.CASCADE,related_name='services')
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    limit = models.SmallIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class Queue(models.Model):
    class StatusChoices(models.TextChoices):
        pending='pending','Pending'
        finished='finished','Finished'
        expired='expired','Expired'
        cancelled='cancelled','Cancelled'
    user=models.ForeignKey('core.User',models.CASCADE,related_name='queue')
    service=models.ForeignKey('core.Service',models.CASCADE,related_name='queue')
    queue_numb=models.SmallIntegerField()
    status=models.CharField(max_length=20,choices=StatusChoices.choices,default=StatusChoices.pending)

class ServiceHistory(models.Model):
    queue=models.ForeignKey('core.Queue',models.CASCADE,related_name='history')




class Notification(models.Model):
    class NotificationTypeChoices(models.TextChoices):
        queue_turn='queue_turn'
        queue_soon='queue_soon',
        queue_created='queue_created'
        queue_expired='queue_expired'
        queue_completed='queue_completed'

    user=models.ForeignKey('core.User',models.CASCADE,related_name='notifications')
    queue=models.ForeignKey('core.Queue',models.CASCADE,related_name='notifications')
    message=models.CharField(max_length=500)
