from django.contrib import admin
from slots import models


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    model = models.Station
    list_display = ('company', 'name')


@admin.register(models.Dock)
class DockAdmin(admin.ModelAdmin):
    model = models.Dock
    fieldsets = (
        (None, {'fields': ('name', 'station')}),
        ('Parameters', {'fields': ('linecount', 'max_slots', 'deadline',
                                   'available_slots')}),
        ('Flags', {'fields': ('multiple_charges', 'has_status', 'has_klv')})
    )

    list_display = ('name', 'station', 'deadline')
