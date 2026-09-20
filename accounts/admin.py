from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import LoginActivity


# =========================================================
# CUSTOM USER ADMIN
# =========================================================

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "date_joined",
        "last_login",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = (
        "-date_joined",
    )


# =========================================================
# LOGIN ACTIVITY ADMIN
# =========================================================

@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "logged_in_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "-logged_in_at",
    )

    readonly_fields = (
        "user",
        "logged_in_at",
    )