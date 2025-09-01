# from django.contrib import admin
# from django.urls import path, include
# from django.views.decorators.csrf import ensure_csrf_cookie
# from django.views.generic import TemplateView
# from drf_spectacular.views import SpectacularAPIView

# urlpatterns = [
#     path("admin/", admin.site.urls),

#     # OpenAPI schema (JSON)
#     path("schema/", SpectacularAPIView.as_view(), name="schema"),

#     # Swagger UI — ensures CSRF cookie is issued
#     path("swagger/", ensure_csrf_cookie(TemplateView.as_view(template_name="swagger-ui.html")), name="swagger-ui"),

#     # API
#     path("api/", include("authentication.urls")),
# ]




# config/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView

urlpatterns = [
    path("admin/", admin.site.urls),

    # OpenAPI schema (JSON)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI — ensures CSRF cookie is issued
    path("swagger/", ensure_csrf_cookie(TemplateView.as_view(template_name="swagger-ui.html")), name="swagger-ui"),

    # --- Simple UI pages (each ensures a CSRF cookie) ---
    path("", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/home.html")), name="ui-home"),
    path("ui/register", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/register.html")), name="ui-register"),
    path("ui/register/verify", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/verify.html")), name="ui-verify"),
    path("ui/login", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/login.html")), name="ui-login"),
    path("ui/me", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/me.html")), name="ui-me"),
    path("ui/logout", ensure_csrf_cookie(TemplateView.as_view(template_name="ui/logout.html")), name="ui-logout"),

    # API
    path("api/", include("authentication.urls")),
]
