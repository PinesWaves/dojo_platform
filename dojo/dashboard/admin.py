from django.contrib import admin
from .models import Dojo, Training


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


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'location', 'training_code')  # Customize columns
    search_fields = ('location', 'training_code')  # Add search fields
    list_filter = ('status', 'date')  # Add filters
    ordering = ('date',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('date', 'status', 'location', 'training_code', 'qr_image')}),
        ('Relations', {'fields': ('attendants', 'techniques')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('date', 'status', 'location', 'training_code', 'qr_image', 'attendants', 'techniques'),
        }),
    )
