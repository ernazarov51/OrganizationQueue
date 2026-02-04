from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import UserRegisterAPIView, OrganizationModelViewSet, accept_organization, ServiceModelViewSet, \
    QueueCreateAPIView, WSTemplateView, ServiceHistoryCreateAPIView

router = DefaultRouter()
router.register('organizations', OrganizationModelViewSet)
router.register('services', ServiceModelViewSet)
urlpatterns = [
    path('register/', UserRegisterAPIView.as_view()),
    path('accept-organization/<int:pk>/', accept_organization),
    path('create-queue/', QueueCreateAPIView.as_view()),
    path('connect/<str:token>/', WSTemplateView.as_view()),
    path('service-user/', ServiceHistoryCreateAPIView.as_view()),
    path('', include(router.urls))

]
