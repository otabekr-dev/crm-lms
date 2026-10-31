from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .serializers import MeSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

User = get_user_model()

class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer)
    def post(self, request:Request) -> Response:    
        serializer = ChangePasswordSerializer(
            data=request.data,
            context = {'request':request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Password changed successfully', status=status.HTTP_200_OK)