from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, Interest, OTPVerification


# =========================================================
# User Profile Inline
# =========================================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0

    # ManyToMany interests will appear as a horizontal selector
    filter_horizontal = ("interests",)


# =========================================================
# User Admin
# =========================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "name",
        "phone_number",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "email",
        "name",
        "phone_number",
    )

    ordering = ("-date_joined",)

    readonly_fields = (
        "date_joined",
        "updated_at",
        "last_login",
    )

    fieldsets = (
        (
            "Account",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "name",
                    "phone_number",
                    "date_of_birth",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone_number",
                    "name",
                    "date_of_birth",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    inlines = [
        UserProfileInline,
    ]


# =========================================================
# User Profile Admin
# =========================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "get_email",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__name",
        "user__email",
        "user__phone_number",
        "bio",
    )

    filter_horizontal = (
        "interests",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "User",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "profile_image",
                    "bio",
                    "interests",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Email")
    def get_email(self, obj):
        return obj.user.email


# =========================================================
# Interest Admin
# =========================================================

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):

    list_display = ("id", "name",)
    search_fields = ("name",)
    ordering = ("name",)