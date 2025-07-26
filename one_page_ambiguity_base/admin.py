from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse


class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "get_button_action",
    )

    @admin.display(description="Action")
    def get_button_action(self, obj):
        return format_html(
            '<a class="btn btn-sm btn-primary" href="{}">Change Access</a>',
            reverse("admin:auth_user_change", args=[obj.id]),
        )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)