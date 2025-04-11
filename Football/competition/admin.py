from django.contrib import admin
from .models import Competition, LeagueTable, LeagueTableEntry, CupStage

class LeagueTableEntryInline(admin.TabularInline):
    model = LeagueTableEntry
    extra = 0

@admin.register(LeagueTable)
class LeagueTableAdmin(admin.ModelAdmin):
    inlines = [LeagueTableEntryInline]
    list_display = ['competition', 'last_updated']

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'type']
    list_filter = ['type', 'country']
    search_fields = ['name', 'country']

@admin.register(CupStage)
class CupStageAdmin(admin.ModelAdmin):
    list_display = ['competition', 'name', 'order']
    list_filter = ['competition', 'name']