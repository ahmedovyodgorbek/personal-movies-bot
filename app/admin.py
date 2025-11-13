from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramUser
from unfold.admin import ModelAdmin


class ReferralInline(admin.TabularInline):
    model = TelegramUser
    fk_name = 'referrer'      # Important: tells Django which field to link
    extra = 0
    fields = ('telegram_id', 'username', 'first_name', 'last_name', 'created_at')
    readonly_fields = fields
    can_delete = False




@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    # Columns displayed in the user list
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "language_code",
        "is_premium",
        "referrer_link",
        "referral_count",
        "created_at",
        "last_activity",
    )
    inlines = [ReferralInline]

    # Columns you can click to view details
    list_display_links = ("telegram_id", "username")

    # Filters on the right sidebar
    list_filter = ("is_premium", "language_code", "created_at")

    # Fields searchable in the search bar
    search_fields = ("telegram_id", "username", "first_name", "last_name", "referrer__username")

    # Readonly fields
    readonly_fields = ("referral_code", "referral_link", "created_at", "last_activity", "referral_count")

    # Optional: group fields in fieldsets for clarity
    fieldsets = (
        ("User Info", {
            "fields": ("telegram_id", "username", "first_name", "last_name", "language_code", "is_premium")
        }),
        ("Referral Info", {
            "fields": ("referrer", "referral_code", "referral_link", "referral_count")
        }),
        ("Timestamps", {
            "fields": ("created_at", "last_activity")
        }),
    )

    # Custom method to display referrer link
    def referrer_link(self, obj):
        if obj.referrer:
            return format_html(
                '<a href="/admin/app/telegramuser/{}/change/">{}</a>',
                obj.referrer.id,
                obj.referrer.username or obj.referrer.telegram_id
            )
        return "-"
    referrer_link.short_description = "Referrer"

    # Optional: enable ordering by fields
    ordering = ("-created_at",)
