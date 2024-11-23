from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id_number', 'first_name', 'last_name', 'email', 'category', 'is_staff', 'is_active')  # Customize columns
    search_fields = ('id_number', 'first_name', 'last_name', 'email')  # Add search fields
    list_filter = ('is_staff', 'is_active', 'category')  # Add filters
    ordering = ('id',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('id_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'category', 'gender', 'level')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_number', 'password1', 'password2', 'first_name', 'last_name', 'email'),
        }),
    )
