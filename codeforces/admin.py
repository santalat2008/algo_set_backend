from django.contrib import admin
from .models import CodeforcesAccount

# Register your models here.
@admin.register(CodeforcesAccount)
class CodeforcesAccountAdmin(admin.ModelAdmin):
    list_display = ("handle", "user", "rating", "max_rating", "last_synced_at")
    search_fields = ("handle", "user__username", "user__email")
    list_filter = ("rank",)