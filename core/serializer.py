from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, IntegerField
from rest_framework.serializers import ModelSerializer, Serializer

from core.models import User, Organization, Service, Queue, ServiceHistory


class UserRegisterModelSerializer(ModelSerializer):
    confirm_password=CharField(write_only=True,required=True)
    class Meta:
        model=User
        fields=['first_name','last_name','username','email','password','confirm_password']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate_password(self,value):
        validate_password(value)
        return value

    def validate(self, attrs):
        confirm_password=attrs['confirm_password']
        password=attrs['password']
        print(password)
        if confirm_password!=password:
            raise ValidationError('Passwords not match')
        attrs.pop('confirm_password')
        return attrs

    def create(self, validated_data):
        password=validated_data['password']
        password=make_password(password)
        validated_data['password']=password
        user=User.objects.create(**validated_data)
        return user


class OrganizationModelSerializer(ModelSerializer):
    class Meta:
        model=Organization
        fields='__all__'
        extra_kwargs={
            'created_at':{'read_only':True},
            'is_accepted':{'read_only':True},
            'owner':{'read_only':True},
        }

    def update(self, instance:Organization, validated_data):
        user=self.context.get('user')
        if instance.owner!=user:
            raise ValidationError('You do not have such permission.')
        instance=super().update(instance,validated_data)
        return instance

    def create(self, validated_data):
        validated_data['owner']=self.context['user']
        organization=Organization.objects.create(**validated_data)
        return organization


class ServiceModelSerializer(ModelSerializer):
    class Meta:
        model=Service
        fields='__all__'
        extra_kwargs={
            'created_at':{'read_only':True}
        }

    def update(self, instance:Service, validated_data):
        user=self.context['user']
        if user!=instance.organization.owner:
            raise ValidationError('You do not have such permission.')
        instance=super().update(instance,validated_data)
        return instance

    def create(self, validated_data):
        user = self.context['user']
        organization=validated_data['organization']
        if user != organization.owner:
            raise ValidationError('You do not have such permission.')
        service=Service.objects.create(**validated_data)
        return service


class QueueModelSerializer(ModelSerializer):
    class Meta:
        model=Queue
        fields='__all__'
        extra_kwargs={
            'queue_numb':{'read_only':True},
            'status':{'read_only':True},
            'user':{'read_only':True}
        }

    def create(self,validated_data):
        user=self.context['user']
        validated_data['user']=user
        max_queue=Queue.objects.aggregate(max_queue=Max('queue_numb'))
        queue_numb=1 if not max_queue['max_queue'] else max_queue['max_queue']+1
        validated_data['queue_numb']=queue_numb
        instance=Queue.objects.create(**validated_data)
        return instance




class ServiceHistoryModelSerializer(ModelSerializer):
    status=CharField(required=True,write_only=True)
    queue_id=IntegerField(required=True,write_only=True)
    class Meta:
        model=ServiceHistory
        fields='__all__'
        extra_kwargs={
            'queue':{'read_only':True}
        }

    def validate(self, attrs):
        status=attrs['status']
        if status not in ('pending','finished','expired','cancelled'):
            raise ValidationError("The status should consist of the following: 'pending','finished','expired','cancelled'")
        queue=Queue.objects.filter(id=attrs['queue_id'])
        if not queue:
            raise ValidationError('queue does not exists')
        return attrs

    def create(self, validated_data):
        queue = Queue.objects.filter(id=validated_data['queue_id']).first()
        status=validated_data['status']
        channel_layer = get_channel_layer()
        message = 'Hello'
        if status == 'finished':
            message = "Your service is finished"
        if status=='expired':
            message="you missed your turn"
        async_to_sync(channel_layer.group_send)(
            f"user_{queue.user.id}",
            {
                "type": "send_notification",
                "data": {
                    "type": "Finished",
                    "message": message,
                    "queue": QueueModelSerializer(queue).data
                }
            }

        )
        next_queue=Queue.objects.filter(id=queue.id+1)
        if next_queue:
            next_queue=next_queue.first()
            async_to_sync(channel_layer.group_send)(
                f"user_{next_queue.user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "type": "GetReady",
                        "message": "Get ready, it's your turn next.",
                        "queue": QueueModelSerializer(next_queue).data
                    }
                }

            )
        instance=ServiceHistory.objects.create(queue=queue)
        return instance
