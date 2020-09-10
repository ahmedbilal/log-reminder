from django.contrib import admin

from .models import Communication, TeamMember, Worklog, Company


class WorklogAdmin(admin.ModelAdmin):
    list_display = ("team_member", "created_at", "pushed")
    list_filter = (
        ("pushed", admin.BooleanFieldListFilter),
        ("created_at", admin.DateFieldListFilter),
    )


class CommunicationInline(admin.TabularInline):
    model = Communication


class TeamMemberInline(admin.TabularInline):
    model = TeamMember


class TeamMemberAdmin(admin.ModelAdmin):
    inlines = [
        CommunicationInline,
    ]


class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        TeamMemberInline,
    ]


admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Worklog, WorklogAdmin)
admin.site.register(Company, CompanyAdmin)
