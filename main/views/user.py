from rest_framework import generics, status
from rest_framework.response import Response
from ..serializers.user import LoginSerializer, ProfileSerializer, RegisterSerializer
from ..models import Session
from django.middleware.csrf import get_token
import uuid
from rest_framework import status
from datetime import timedelta
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.timezone import now


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_user = serializer.save()

        token = str(uuid.uuid4())
        expires_at = now() + timedelta(days=2)

        session = Session.objects.create(
            user=new_user,
            session_token=token,
            expires_at=expires_at,
        )

        user_data = ProfileSerializer(new_user).data

        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            'sessionId', session.session_token, expires=expires_at
        )
        csrf_token = get_token(request)
        response['X-CSRFToken'] = csrf_token

        return response

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        csrf_token = get_token(request)

        user = serializer.validated_data

        token = str(uuid.uuid4())
        user.last_login = now()
        user.save()

        expires_at = now() + timedelta(days=2)

        session = Session.objects.create(
            user=user,
            session_token=token,
            expires_at=expires_at,
        )
        
        user_data = ProfileSerializer(user).data
        
        response = Response(user_data, status=status.HTTP_200_OK)
        response.set_cookie(
            'sessionId',
            session.session_token,
            expires=expires_at, 
        )
        response['X-CSRFToken'] = csrf_token
        return response

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        sessions = Session.objects.filter(user_id=user)
        response = Response({'details': 'Logged out successfully'}, status=status.HTTP_200_OK)
        if sessions:
            sessions.delete()
            response.delete_cookie('sessionId')
        else:
            response = Response({'details': 'Invalid session token'}, status=status.HTTP_400_BAD_REQUEST)
            
        return response

class ProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileSerializer(user)

        return Response(serializer.data)