from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Dojo

@admin.register(Dojo)
class DojoAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'sensei', 'description')  # Customize columns
    search_fields = ('name', 'image', 'description')  # Add search fields
    # list_filter = ('name', 'sensei')  # Add filters
    ordering = ('name',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('name', 'sensei')}),
        ('Info', {'fields': ('image', 'description', 'students')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'image', 'sensei', 'description'),
        }),
    )
