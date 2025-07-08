from django.contrib import admin
from .models import SentSMS
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(SentSMS)
class SentSMSAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "message", "status", "sent_at")
    ordering = ("-sent_at",)
    list_filter = ("status", "sent_at")
    search_fields = ("phone_number", "message")

    def get_model_perms(self, request):
        """
        Hide this model from the default 'Common' group in the sidebar.
        We'll override it below to customize grouping.
        """
        return super().get_model_perms(request)

    def get_admin_site(self, request):
        return super().get_admin_site(request)

    def get_queryset(self, request):
        return super().get_queryset(request)

    class Meta:
        verbose_name = "Sent SMS"
        verbose_name_plural = "Sent SMS messages"
        
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Add phone_number to fieldsets so it appears when editing a user
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {"fields": ("phone_number",)}),
    )

    # Add phone_number when creating a user via the admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra Fields", {"fields": ("phone_number",)}),
    )

    # Show phone number in the user list
    list_display = ["username", "email", "phone_number", "is_staff", "is_superuser"]
