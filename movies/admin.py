from django.contrib import admin
from unfold.admin import ModelAdmin

from . import models
from django import forms
from django.contrib import admin
from datetime import timedelta
import re



@admin.register(models.MovieGenres)
class MovieGenresAdmin(ModelAdmin):
    list_display = ("title",)

@admin.register(models.PartnerChannels)
class MovieGenresAdmin(ModelAdmin):
    list_display = ("title",)
    

@admin.register(models.Movies)
class MoviesAdmin(ModelAdmin):
    list_display = (
        "id",
        "title",
        "type",
        "release_date",
        "rating",
        "duration",
        "genre_list",
        "actors",
        "created_at"
    )
    list_filter = ("type", "release_date", "rating", "genres", "created_at")
    search_fields = ("title", "description", "genres__title", "actors")
    # prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug","short_description")
    ordering = ("-release_date", "title", "created_at")
    filter_vertical = ("genres",)
    list_per_page = 25

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "title",
                "slug",
                "description",
                "short_description",
                "type",
                "release_date",
                "duration",
                "rating",
                "actors"
            )
        }),
        ("Relations", {
            "fields": ("genres",),
            "classes": ("collapse",),
        }),
        ("Media & Links", {
            "fields": ("telegram_link", "image"),
            "classes": ("collapse",),
        }),
    )

    # @admin.display(description="Image Preview")
    # def image_preview(self, obj):
    #     if obj.image:
    #         return format_html(
    #             '<img src="{}" width="90" height="130" style="border-radius:6px;object-fit:cover;" />',
    #             obj.image.url
    #         )
    #     return "—"

    @admin.display(description="Genres")
    def genre_list(self, obj):
        return obj.genre_list()


