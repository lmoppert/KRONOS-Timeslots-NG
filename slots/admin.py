from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from slots import models


class RoleInline(admin.TabularInline):
    model = models.Role
    extra = 1


class ProfileInline(admin.TabularInline):
    model = models.Profile


class JobInline(admin.TabularInline):
    model = models.Job


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    model = models.Company


@admin.register(models.Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    model = models.Deadline
    list_display = ('name', 'booking_deadline', 'rnvp')


@admin.register(models.Station)
class StationAdmin(admin.ModelAdmin):
    model = models.Station
    list_display = ('__str__', 'description')
    inlines = [RoleInline, ]


@admin.register(models.Dock)
class DockAdmin(admin.ModelAdmin):
    model = models.Dock
    fieldsets = (
        (None, {
            'fields': ('name', 'station')}),
        ('Parameters', {
            'fields': ('linecount', 'max_slots', 'slotlength', 'deadline')}),
        ('Flags', {
            'fields': ('multiple_charges', 'has_status', 'has_klv')}),
        ('Timeslots', {
            'fields': ('available_slots', )}),
    )
    readonly_fields = ('available_slots', )
    list_display = ('__str__', 'deadline')


@admin.register(models.Slot)
class SlotAdmin(admin.ModelAdmin):
    model = models.Slot
    list_display = ('dock', 'date', 'index', 'line', 'user')
    readonly_fields = ('dock', 'date', 'index', 'line', 'user')
    inlines = [JobInline, ]


# Reconfigure User Admin
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    inlines = [RoleInline, ProfileInline]
