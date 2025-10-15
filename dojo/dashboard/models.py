import re

from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.utils import timezone
from secrets import token_urlsafe

from user_management.models import User, Category
from utils.utils import generate_qr_file


LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]


class Dojo(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    description = models.TextField()
    sensei: User = models.OneToOneField(User, related_name="sensei", on_delete=models.DO_NOTHING)
    students = models.ManyToManyField(User, related_name="students", blank=True)
    dojo_location = models.CharField(max_length=100, default='', null=False, blank=False)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(max_length=255, default='', null=False, blank=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    def clean(self):
        """
        Ensure that the 'sensei' is a user with category SENSEI.
        """
        if self.sensei and self.sensei.category != Category.SENSEI:
            raise ValidationError("The selected user must have the category 'SENSEI'.")

    def save(self, *args, **kwargs):
        """
        Call clean() to enforce validation before saving.
        """
        self.clean()
        super().save(*args, **kwargs)


class Kata(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    embusen_diagram = models.ImageField(upload_to='embusen/', blank=True, null=True)
    video_reference = models.URLField(blank=True, null=True)
    order = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class KataSerie(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='series/', blank=True, null=True)
    katas = models.ManyToManyField(Kata, related_name='series')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class KataLesson(models.Model):
    kata = models.ForeignKey(Kata, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=100)
    objectives = models.TextField()
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.kata.name} - {self.title}"


class KataLessonActivity(models.Model):
    lesson = models.ForeignKey(KataLesson, on_delete=models.CASCADE, related_name='activities')
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='activities/images/', blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class KataLessonActivityImage(models.Model):
    activity = models.ForeignKey(KataLessonActivity, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='activities/images/')
    caption = models.TextField(blank=True)

    def __str__(self):
        return f"Imagen de {self.activity.title}"


class KataLessonActivityVideo(models.Model):
    activity = models.ForeignKey(KataLessonActivity, on_delete=models.CASCADE, related_name='videos')
    url = models.URLField()
    description = models.TextField(blank=True)

    @property
    def embed_url(self):
        if "youtube.com" in self.url or "youtu.be" in self.url:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.url)
            if 'shorts' in parsed.path:  # Handle YouTube Shorts URLs
                video_id = parsed.path.split('/')[2]
                return f"https://www.youtube.com/embed/{video_id}"
            if parsed.netloc == 'youtu.be':  # Handle shortened YouTube URLs
                video_id = parsed.path[1:]
                return f"https://www.youtube.com/embed/{video_id}"
            if parsed.path.startswith('/embed/'):  # Already an embed URL
                return self.url
            video_id = parse_qs(parsed.query).get('v')
            if video_id:
                return f"https://www.youtube.com/embed/{video_id[0]}"
        elif "drive.google.com" in self.url:
            match = re.search(r'/d/([a-zA-Z0-9_-]+)', self.url)
            if match:
                file_id = match.group(1)
                return f"https://drive.google.com/file/d/{file_id}/preview"
            return ""
        return None

    def __str__(self):
        return f"Video de {self.activity.title}"


class Kumite(models.Model):
    """Types of kumite (ippon, sanbon, jiyu, etc.)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    video_reference = models.URLField(blank=True, null=True)
    order = models.CharField(max_length=3)

    def __str__(self):
        return self.name


class TechniqueType(models.TextChoices):
    JOINT = 'CA', 'Joint Warm-Up'
    STRETCH = 'ES', 'Stretching'
    KIHON = 'KI', 'Kihon'
    KATA = 'KA', 'Kata'
    KUMITE = 'KU', 'Kumite'


class TechniqueLevel(models.TextChoices):
    BEGINNER = 'PR', 'Beginner'
    INTERMEDIATE = 'IN', 'Intermediate'
    ADVANCED = 'AV', 'Advanced'


class Technique(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='techniques/',
        blank=True,
        null=True,
        default='techniques/default_technique.jpg'
    )
    type = models.CharField(max_length=2,choices=TechniqueType.choices,default=TechniqueType.KIHON)
    level = models.CharField(max_length=2, choices=TechniqueLevel.choices, blank=True, null=True)

    def __str__(self):
        return self.name


class TrainingStatus(models.TextChoices):
    SCHEDULED = "S", "Scheduled"
    ONGOING = "O", "On Going"
    FINISHED = "F", "Finished"
    CANCELED = "C", "Canceled"


class TrainingType(models.TextChoices):
    KATA = "KATA", "Kata"
    KUMITE = "KUMITE", "Kumite"
    TECHNIQUE = "TECH", "Technique"
    PHYSICAL = "PHYS", "Physical Preparation"
    MIXED = "MIXED", "Mixed"


class Training(models.Model):
    date = models.DateTimeField(auto_now=False)
    type = models.CharField(choices=TrainingType.choices, default=TrainingType.MIXED, max_length=10)
    status = models.CharField(choices=TrainingStatus.choices, default=TrainingStatus.SCHEDULED, max_length=2)
    techniques = models.ManyToManyField('Technique', related_name='trainings', blank=True)
    details = models.TextField(blank=True, null=True, help_text="Comentarios o detalles adicionales.")
    location = models.CharField(max_length=100, default='')
    katas = models.ManyToManyField(Kata, blank=True, related_name="trainings")
    kumites = models.ManyToManyField(Kumite, blank=True, related_name="trainings")

    def __str__(self):
        return f"Training on {self.date.strftime('%Y-%m-%d %H:%M')} - {self.get_status_display()}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Training"
        verbose_name_plural = "Trainings"


class DayChoices(models.TextChoices):
    MONDAY = 'MON', 'Monday'
    TUESDAY = 'TUE', 'Tuesday'
    WEDNESDAY = 'WED', 'Wednesday'
    THURSDAY = 'THU', 'Thursday'
    FRIDAY = 'FRI', 'Friday'
    SATURDAY = 'SAT', 'Saturday'
    SUNDAY = 'SUN', 'Sunday'

class TrainingScheduling(models.Model):

    # dojo = models.ForeignKey(Dojo, on_delete=models.CASCADE, related_name="training_schedules")
    day_of_week = models.CharField(
        choices=DayChoices.choices,
        default=DayChoices.MONDAY,
        max_length=3
    )
    time = models.TimeField()
    # location = models.CharField(max_length=100, default='')
    training = models.ForeignKey('Training', on_delete=models.CASCADE)
    details = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("day_of_week", "time", "training")
        ordering = ["day_of_week", "time"]
        verbose_name = "Automatic Training Schedule"
        verbose_name_plural = "Automatic Training Schedules"

    def __str__(self):
        return f"{self.get_day_of_week_display()} at {self.time.strftime('%H:%M')}"


class AttendanceStatus(models.TextChoices):
    PRESENT = "P", "Present"
    ABSENT = "A", "Absent"
    LATE = "L", "Late"
    EXCUSED = "E", "Excused"


class Attendance(models.Model):
    training = models.ForeignKey("Training", on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    status = models.CharField(max_length=1, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time at which attendance was recorded."
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("training", "student")
        ordering = ["-timestamp"]
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"

    def __str__(self):
        return f"{self.student} - {self.training.date.strftime('%Y-%m-%d')} ({self.get_status_display()})"
