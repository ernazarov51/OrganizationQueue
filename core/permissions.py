from rest_framework.permissions import BasePermission

from core.models import Queue, Employee


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff

class IsEmployeePermission(BasePermission):
    def has_permission(self, request, view):
        queue:Queue=Queue.objects.filter(id=request.data['queue_id'])
        if not queue:
            return False
        employee:Employee=Employee.objects.filter(id=request.user.id)
        if not employee:
            return False
        if queue.service.organization!=employee.organization:
            return False
        return True

