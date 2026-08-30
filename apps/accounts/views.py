from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .serializers import RegisterSerializer, MeSerializer
from django.contrib.auth import get_user_model
from core.permissions import IsAdmin

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [IsAdmin]
    
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'msg':"Ro'yxatdan o'tdingiz",
                    'username':user.username,
                    'id':user.id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
    