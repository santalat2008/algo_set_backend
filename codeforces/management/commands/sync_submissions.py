from django.core.management.base import BaseCommand

from codeforces.models import CodeforcesAccount
from codeforces.services import CodeforcesAPIError
from codeforces.submission_services import sync_user_submissions


class Command(BaseCommand):
    help = "Sync submissions for all connected Codeforces accounts"

    def handle(self, *args, **options):
        accounts = list(
            CodeforcesAccount.objects.all().order_by("id")
        )
        total = len(accounts)

        if total == 0:
            self.stdout.write(
                self.style.WARNING("Ulangan Codeforces akkauntlari yo'q.")
            )
            return

        success_count = 0
        failure_count = 0

        self.stdout.write(f"Sinxronlash boshlanmoqda: {total} ta akkaunt.")

        for account in accounts:
            try:
                count = sync_user_submissions(account)
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{account.handle}: {count} ta submission qayta ishlandi."
                    )
                )
            except (CodeforcesAPIError, Exception) as exc:
                failure_count += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"{account.handle}: sinxronlash xatosi: {exc}"
                    )
                )

        self.stdout.write(
            f"Tugadi. Muvaffaqiyatli: {success_count}; xatolar: {failure_count}."
        )
