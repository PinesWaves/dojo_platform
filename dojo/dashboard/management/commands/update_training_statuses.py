from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Training, TrainingStatus


class Command(BaseCommand):
    help = "Update training statuses: SCHEDULED → ONGOING → FINISHED based on date and duration."

    def handle(self, *args, **options):
        now = timezone.now()

        # SCHEDULED → ONGOING: training has started but not yet finished
        started = Training.objects.filter(
            status=TrainingStatus.SCHEDULED,
            date__lte=now,
        )
        started_count = started.update(status=TrainingStatus.ONGOING)

        # ONGOING → FINISHED: training start + duration has passed
        ongoing = Training.objects.filter(status=TrainingStatus.ONGOING)
        finished_count = 0
        for training in ongoing:
            if now >= training.date + training.duration:
                training.status = TrainingStatus.FINISHED
                training.save(update_fields=['status'])
                finished_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {started_count} training(s) to ONGOING, "
                f"{finished_count} training(s) to FINISHED."
            )
        )
