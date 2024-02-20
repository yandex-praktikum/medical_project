from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import (
    MedicalCard,
    User,
)


@admin.register(User)
class BaseUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("role",)
    list_filter = UserAdmin.list_filter + ("role",)
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


@admin.register(MedicalCard)
class MedicalCardAdmin(admin.ModelAdmin):
    pass
