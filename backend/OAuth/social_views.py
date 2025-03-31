import requests

from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render

from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import User
import json


def google_auth(request):
    """Перенаправление на Google OAuth"""
    redirect_uri = request.build_absolute_uri(reverse("google-callback"))
    scope = "openid email profile"

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&"
        f"client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"state={settings.SECRET_KEY}"  # Для простой проверки state
    )

    return redirect(auth_url)


def google_callback(request):
    """Обработчик callback от Google"""
    code = request.GET.get("code")
    state = request.GET.get("state")
    error = request.GET.get("error")

    if error:
        return render(request, "error.html", {"error": error})

    # Простая проверка state
    if state != settings.SECRET_KEY:
        return JsonResponse({"error": "Invalid state"}, status=400)

    # Обмен code на access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        "redirect_uri": request.build_absolute_uri(reverse("google-callback")),
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    if "error" in token_data:
        return JsonResponse(token_data, status=400)

    # Получение информации о пользователе
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f'Bearer {token_data["access_token"]}'},
    ).json()

    # Создание/получение пользователя
    user, created = User.objects.get_or_create(
        email=user_info["email"],
        defaults={
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
            "is_active": True,
        },
    )

    # Генерация JWT токенов
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    # Перенаправление с токенами в URL
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "email": user.email,
    }
    if tokens:
        return render(
            request,
            "google/google_login.html",
            {"tokens": json.dumps(tokens, indent=2)},
        )


def google_login_page(request):
    """Главная страница для входа"""
    return render(request, "google/google_login.html")
