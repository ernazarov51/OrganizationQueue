from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.models import User, Organization, Service, Queue, ServiceHistory
from core.permissions import IsAdmin, IsEmployeePermission
from core.serializer import UserRegisterModelSerializer, OrganizationModelSerializer, ServiceModelSerializer, \
    QueueModelSerializer, ServiceHistoryModelSerializer


# Create your views here.
@extend_schema(tags=['api'])
class UserRegisterAPIView(CreateAPIView):
    serializer_class = UserRegisterModelSerializer
    queryset = User.objects.all()

class OrganizationModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Organization.objects.all()
    serializer_class = OrganizationModelSerializer

    def get_serializer_context(self):
        c=super().get_serializer_context()
        c['user']=self.request.user
        return c

    def perform_destroy(self, instance):
        if self.request.user!=instance.owner:
            raise ValidationError('You do not have such permission.')
        instance.delete()

@api_view(['GET'])
@extend_schema(tags=['organizations'])
@permission_classes([IsAuthenticated,IsAdmin])
def accept_organization(request,pk):
    if request.method=='GET':
        organization:Organization=get_object_or_404(Organization,id=pk)
        organization.is_accepted=1
        organization.save()
        serializer=OrganizationModelSerializer(organization)
        return JsonResponse(serializer.data)

class ServiceModelViewSet(ModelViewSet):
    permission_classes([IsAuthenticated])
    queryset = Service.objects.all()
    serializer_class = ServiceModelSerializer
    def get_serializer_context(self):
        c=super().get_serializer_context()
        c['user']=self.request.user
        return c


    def perform_destroy(self, instance):
        if self.request.user!=instance.organization.owner:
            raise ValidationError('You do not have such permission.')
        instance.delete()


class QueueCreateAPIView(CreateAPIView):
    serializer_class = QueueModelSerializer
    queryset = Queue.objects.all()
    def get_serializer_context(self):
        c=super().get_serializer_context()
        c['user']=self.request.user
        return c


class ServiceHistoryCreateAPIView(CreateAPIView):
    serializer_class =ServiceHistoryModelSerializer
    queryset = ServiceHistory.objects.all()









class WSTemplateView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        token = self.kwargs.get('token')
        context['token'] = token
        return context








