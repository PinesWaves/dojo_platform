from django.contrib import admin
from .models import Dojo, Training, KataSerie, Kata, KataLesson, KataLessonActivity, KataLessonActivityImage, \
    KataLessonActivityVideo, Attendance, ActivityCompletion, LessonCompletion


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


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    inlines = [AttendanceInline]
    list_display = ('date', 'type', 'status', 'location')  # Customize columns
    search_fields = ('date', 'location')  # YYYY-MM-DDsearch_fields = ('date', 'location')  # YYYY-MM-DD
    search_help_text = "Search by date using the format YYYY-MM-DD"
    list_filter = ('status', 'date')  # Add filters
    ordering = ('date',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('date', 'status', 'location')}),
        ('Relations', {'fields': ('techniques', 'katas', 'kumites')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('date', 'status', 'location'),
        }),
    )


@admin.register(Kata)
class KataAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'level', 'order')  # Customize columns
    search_fields = ('name', 'description')  # Add search fields
    ordering = ('order',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('name', 'description', 'level', 'embusen_diagram', 'video_reference', 'order')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'description', 'level', 'embusen_diagram', 'video_reference', 'order'),
        }),
    )


@admin.register(KataSerie)
class KataSerieAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Customize columns
    search_fields = ('name', 'description')  # Add search fields
    ordering = ('name',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('name', 'katas', 'description', 'image')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'katas', 'description', 'image'),
        }),
    )


@admin.register(KataLesson)
class KataLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'kata', 'order')  # Customize columns
    search_fields = ('title', 'kata__name')  # Add search fields
    ordering = ('order',)  # Default ordering
    fieldsets = (
        (None, {'fields': ('title', 'kata', 'objectives', 'content', 'order')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'kata', 'objectives', 'content', 'order'),
        }),
    )

class KataLessonActivityImageInline(admin.TabularInline):
    model = KataLessonActivityImage
    extra = 1
    fields = ('image', 'caption')

class KataLessonActivityVideoInline(admin.TabularInline):
    model = KataLessonActivityVideo
    extra = 1
    fields = ('url', 'description')

@admin.register(KataLessonActivity)
class KataLessonActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson',  'order')  # Customize columns
    search_fields = ('title', 'lesson__title')  # Add search fields
    ordering = ('order',)  # Default ordering
    inlines = [KataLessonActivityImageInline, KataLessonActivityVideoInline]
    fieldsets = (
        (None, {'fields': ('title', 'lesson', 'description', 'order')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'lesson', 'description', 'order'),
        }),
    )


@admin.register(ActivityCompletion)
class ActivityCompletionAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'completed_at')
    list_filter = ('completed_at', 'activity__lesson__kata')
    search_fields = ('student__first_name', 'student__last_name', 'activity__title')
    readonly_fields = ('completed_at',)
    date_hierarchy = 'completed_at'
    ordering = ('-completed_at',)


@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed_at')
    list_filter = ('completed_at', 'lesson__kata')
    search_fields = ('student__first_name', 'student__last_name', 'lesson__title')
    readonly_fields = ('completed_at',)
    date_hierarchy = 'completed_at'
    ordering = ('-completed_at',)
