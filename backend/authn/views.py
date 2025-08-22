import secrets, datetime as dt, httpx
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .spotify import authorize_url, exchange_code
from .crypto import encrypt_refresh
from .models import OAuthToken

User = get_user_model()

@require_GET
def spotify_login(request):
    state = secrets.token_urlsafe(24)
    request.session["spotify_state"] = state
    return HttpResponseRedirect(authorize_url(state))

@require_GET
def spotify_callback(request):
    if request.GET.get("error"):
        return JsonResponse({"error": request.GET["error"]}, status=400)
    state, code = request.GET.get("state"), request.GET.get("code")
    if not state or state != request.session.get("spotify_state"):
        return JsonResponse({"error": "invalid_state"}, status=400)

    tokens = exchange_code(code)
    access, refresh = tokens["access_token"], tokens.get("refresh_token")
    expires_in = int(tokens.get("expires_in", 3600))

    me = httpx.get("https://api.spotify.com/v1/me",
                   headers={"Authorization": f"Bearer {access}"},
                   timeout=20).json()
    username = f"sp_{me['id']}"
    user, _ = User.objects.get_or_create(username=username,
                                         defaults={"email": me.get("email","")})

    obj, _ = OAuthToken.objects.get_or_create(user=user, provider="spotify")
    obj.access_token = access
    if refresh: obj.refresh_enc = encrypt_refresh(refresh)
    obj.expires_at = timezone.now() + dt.timedelta(seconds=expires_in)
    obj.scope = tokens.get("scope","")
    obj.save()

    login(request, user)  # issues httpOnly session cookie
    return redirect("http://localhost:5173/")

@require_POST
def auth_logout(request):
    logout(request)
    return JsonResponse({"ok": True})

@login_required
def me(request):
    return JsonResponse({
      "username": request.user.username,
      "email": getattr(request.user, "email",""),
      "connected_to_spotify": OAuthToken.objects.filter(user=request.user, provider="spotify").exists(),
    })
