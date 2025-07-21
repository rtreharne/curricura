from django.contrib import admin
from .models import Institution, School, Profile


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "created_at")
    list_filter = ("institution",)
    search_fields = ("name", "institution__name")
    ordering = ("institution__name", "name")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "get_schools")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    filter_horizontal = ("schools",)

    def get_schools(self, obj):
        return ", ".join([school.name for school in obj.schools.all()])
    get_schools.short_description = "Schools"
