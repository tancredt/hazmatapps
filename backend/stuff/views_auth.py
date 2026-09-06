from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  # <--- Required to read .env variables
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    """Standard username/password login."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            if not username or not password:
                return Response({"success": False, "message": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response({"success": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            login(request, user)
            return Response({"success": True, "message": "Login successful", "user": user_payload(user)}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"success": False, "message": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name="dispatch")
class PinLoginView(APIView):
    """PIN-based login for the Location Changer App."""
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            pin = request.data.get("pin")
            if not pin or len(str(pin)) != 4 or not str(pin).isdigit():
                return Response({"success": False, "message": "A valid 4-digit PIN is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch securely from server-side settings (.env)
            username = getattr(settings, "PIN_LOGIN_USERNAME", "DistrictCache")
            password_prefix = getattr(settings, "PIN_LOGIN_PASSWORD_PREFIX", "District!")
            password = f"{password_prefix}{pin}"
            
            # --- ADD THIS DEBUG LINE ---
            print(f"🔍 DEBUG PIN LOGIN: Attempting auth with Username='{username}' and Password='{password}'")
            # ---------------------------
            
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                return Response({"success": False, "message": "Invalid PIN"}, status=status.HTTP_401_UNAUTHORIZED)
                
            login(request, user)
            return Response({"success": True, "message": "Login successful", "user": user_payload(user)}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"success": False, "message": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logout(request)
            return Response({"success": True, "message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"success": False, "message": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrentUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            user = getattr(request._request, "user", None)
        if user and user.is_authenticated:
            return Response({"authenticated": True, "user": user_payload(user)}, status=status.HTTP_200_OK)
        return Response({"authenticated": False, "user": None}, status=status.HTTP_200_OK)

class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)
        return Response({"csrfToken": csrf_token}, status=status.HTTP_200_OK)
