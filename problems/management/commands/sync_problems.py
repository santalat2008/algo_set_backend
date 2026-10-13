from django.core.management.base import BaseCommand, CommandError

from problems.services import sync_problems


class Command(BaseCommand):
    help = "Sync the Codeforces problem catalog"

    def handle(self, *args, **options):
        try:
            count = sync_problems()
        except Exception as exc:
            raise CommandError(
                f"Masalalarni sinxronlash muvaffaqiyatsiz: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Sinxronlash yakunlandi. Qayta ishlangan masalalar: {count}"
            )
        )
