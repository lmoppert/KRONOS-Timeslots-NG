from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from slots import models


class RoleInline(admin.TabularInline):
    model = models.Role
    extra = 1


@admin.register(models.Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    model = models.Deadline
    list_display = ('name', 'booking_deadline', 'rnvp')


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    model = models.Station
    list_display = ('company', 'name')
    inlines = [RoleInline, ]


@admin.register(models.Dock)
class DockAdmin(admin.ModelAdmin):
    model = models.Dock
    fieldsets = (
        (None, {'fields': ('name', 'station')}),
        ('Parameters', {'fields': ('linecount', 'max_slots', 'deadline')}),
        ('Flags', {'fields': ('multiple_charges', 'has_status', 'has_klv')})
    )

    list_display = ('name', 'station', 'deadline')


# Reconfigure User Admin
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    inlines = [RoleInline, ]
