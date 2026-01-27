import yaml
import shutil
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import connection

from dashboard.models import (
    Kata, KataSerie, KataLesson, KataLessonActivity,
    KataLessonActivityImage, KataLessonActivityVideo, Kumite
)
from dojo.settings import BASE_DIR

BASE_PATH = BASE_DIR / "utils" / "library_data"
KATAS_FILE = BASE_PATH / "katas.yaml"
SERIES_FILE = BASE_PATH / "series.yaml"
LESSONS_FILE = BASE_PATH / "lessons" / "heian_shodan_lessons.yaml"
KUMITE_FILE = BASE_PATH / "kumite.yaml"

# TODO: Add JKA historical data (Gasshuku, championships,) etc.)
class Command(BaseCommand):
    help = "Load Katas, Series and Lessons from YAML file"

    def handle(self, *args, **options):
        Kata.objects.all().delete()
        KataSerie.objects.all().delete()
        KataLesson.objects.all().delete()
        KataLessonActivity.objects.all().delete()
        KataLessonActivityImage.objects.all().delete()
        for img_obj in KataLessonActivityImage.objects.all():
            if img_obj.image and img_obj.image.path:
                Path(img_obj.image.path).unlink(missing_ok=True)
        KataLessonActivityImage.objects.all().delete()
        KataLessonActivityVideo.objects.all().delete()
        Kumite.objects.all().delete()

        # Reset primary key sequences
        with connection.cursor() as cursor:
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_kata', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_katalesson', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_kataserie', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_katalessonactivity', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_katalessonactivityimage', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_katalessonactivityvideo', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_kataserie_katas', 'id'), 1, false);")
            cursor.execute("SELECT setval(pg_get_serial_sequence('dashboard_kumite', 'id'), 1, false);")

        self.stdout.write(self.style.WARNING("📂 Loading Katas data..."))

        # --- LOAD FILES INFO ---
        with open(KATAS_FILE, "r", encoding="utf-8") as kaf, \
            open(SERIES_FILE, "r", encoding="utf-8") as sef, \
            open(LESSONS_FILE, "r", encoding="utf-8") as lf, \
            open(KUMITE_FILE, "r", encoding="utf-8") as kuf:
            katas_data = yaml.safe_load(kaf)
            series_data = yaml.safe_load(sef)
            lessons_data = yaml.safe_load(lf)
            kumite_data = yaml.safe_load(kuf)

        # --- KATAS ---
        katas = {}
        # TODO : load summary info
        ka_summary = katas_data['summary']
        ka_data = katas_data['katas']
        for item in ka_data:
            kata, _ = Kata.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item.get("description", ""),
                    "level": item.get("level", "beginner"),
                    "video_reference": item.get("video_reference"),
                    "order": item.get("order", 1),
                },
            )
            katas[item["name"]] = kata
            self.stdout.write(self.style.SUCCESS(f"✅ Kata loaded: {kata.name}"))

        # --- SERIES ---
        ssdata = series_data['series']
        for serie in ssdata:
            serie_obj, _ = KataSerie.objects.get_or_create(
                name=serie["name"],
                defaults={"description": serie.get("description", "")},
            )
            for kata_name in serie.get("katas", []):
                if kata_name in katas:
                    serie_obj.katas.add(katas[kata_name])
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded series: {serie_obj.name}"))

        # --- LESSONS ---
        lsdata = lessons_data['lessons']
        for lesson in lsdata:
            kata_name = lesson["kata"]
            kata = katas.get(kata_name)
            if not kata:
                self.stdout.write(self.style.ERROR(f"❌ Kata not found for lesson: {kata_name}"))
                continue

            lesson_obj, _ = KataLesson.objects.get_or_create(
                kata=kata,
                title=lesson["title"],
                defaults={
                    "objectives": lesson.get("objectives", []),
                    "content": lesson.get("content", []),
                    "order": lesson.get("order", 1),
                },
            )

            activities = lesson.get("activities", [])
            activities = activities if activities else []
            for activity in activities:
                activity_obj, _ = KataLessonActivity.objects.get_or_create(
                    lesson=lesson_obj,
                    title=activity["title"],
                    defaults={
                        "description": activity.get("description", ""),
                        "order": activity.get("order", 1),
                    },
                )

                # --- IMAGES ---
                images = activity.get("images", [])
                images = images if images else []
                for img in images:
                    img_path = img.get("path")
                    if img_path:
                        src_path = BASE_PATH / img_path
                        if src_path.exists():

                            with open(src_path, "rb") as f:
                                KataLessonActivityImage.objects.get_or_create(
                                    activity=activity_obj,
                                    title=img.get("title", ""),
                                    defaults={
                                        "caption": img.get("caption", ""),
                                        "image": File(f, name=src_path.name),
                                    }
                                )
                            self.stdout.write(self.style.SUCCESS(f"🖼 Image loaded: {src_path.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"⚠️ Image not found: {src_path}"))

                # --- VIDEOS ---
                videos = activity.get("videos", [])
                videos = videos if videos else []
                for vid in videos:
                    KataLessonActivityVideo.objects.get_or_create(
                        activity=activity_obj,
                        url=vid["url"],
                        defaults={"description": vid.get("description", "")},
                    )

            self.stdout.write(self.style.SUCCESS(f"✅ Lesson loaded: {lesson_obj.title}"))

        # --- KUMITES ---
        kumites = {}
        # TODO : load summary info
        ku_summary = kumite_data['summary']
        ku_data = kumite_data['katas']
        for item in ku_data:
            kumite, _ = Kumite.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item.get("description", ""),
                    "level": item.get("level", "beginner"),
                    "video_reference": item.get("video_reference"),
                    "order": item.get("order", 1),
                },
            )
            kumites[item["name"]] = kumite
            self.stdout.write(self.style.SUCCESS(f"✅ Kumite loaded: {kumite.name}"))

        self.stdout.write(self.style.SUCCESS("🎉 Data loaded correctly."))
