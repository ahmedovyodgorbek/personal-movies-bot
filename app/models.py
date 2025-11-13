import uuid
from django.db import models
from django.core.exceptions import ValidationError


BOT_USERNAME = "AhmedovMoviesBot"

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    # 🔗 Referral system
    referrer = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals"
    )
    referral_code = models.CharField(
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    def __str__(self):
        return f"{self.first_name or ''} @{self.username or self.telegram_id}"

    @property
    def referral_link(self):
        return f"https://t.me/{f"{BOT_USERNAME}"}?start=ref_{self.referral_code}"

    @property
    def referral_count(self):
        return self.referrals.count()
    
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "Users"
