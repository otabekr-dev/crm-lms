from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied


class BaseViewSet(ModelViewSet):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.user.is_authenticated  and request.user.must_change_password:
            if request.path != '/api/accounts/change-password/':
                raise PermissionDenied('Avval parolni o\'zgartiring')