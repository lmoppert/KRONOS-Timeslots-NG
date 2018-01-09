# from datetime import timedelta, datetime, time
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.db import models


class Deadline(models.Model):
    name = models.CharField(max_length=50)
    booking_deadline = models.TimeField(
        default='00:00:00',
        help_text=_(
            "Booking deadline = time on the day before from which on a slot "
            "can not be reserved any more. Set this to midnight to turn off "
            "this feature completely for this station"
        )
    )
    rnvp = models.TimeField(
        default='00:00:00',
        help_text=_(
            "RVNP = Rien ne vas plus -- time when a slot can not be edited "
            "any more, set to Midnight to have the deadline as RNVP"
        )
    )

    # def past_deadline(self, curr_date, curr_time):
    #     my_dl = self.booking_deadline
    #     if my_dl == time(0, 0):
    #         deadline = datetime.combine(curr_date + timedelta(days=1), my_dl)
    #     else:
    #         deadline = datetime.combine(curr_date - timedelta(days=1), my_dl)
    #     return curr_time > deadline

    def __str__(self):
        return "{} ({} / {})".format(self.name, self.booking_deadline,
                                     self.rnvp)

    class Meta:
        verbose_name = _("Deadline")
        verbose_name_plural = _("Deadlines")


class Station(models.Model):
    company = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return "{} - {}".format(self.company, self.name)

    class Meta:
        verbose_name = _("Station")
        verbose_name_plural = _("Stations")


class Dock(models.Model):
    name = models.CharField(max_length=200)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    linecount = models.IntegerField(default=1)
    available_slots = JSONField(default=[[], [], [], [], [], [], []])
    max_slots = models.IntegerField(default=0, help_text=_("0 for unlimited"))
    deadline = models.ForeignKey(Deadline, default=1, on_delete=models.CASCADE)
    multiple_charges = models.BooleanField(
        default=True,
        help_text=_(
            "If this option is marked, the reservation form offers the "
            "opportunity to add more than one job"
        )
    )
    has_status = models.BooleanField(
        default=False,
        help_text=_(
            "This option adds a Statusbar to the job view, which shows the "
            "current loading status"
        )
    )
    has_klv = models.BooleanField(
        default=False,
        help_text=_(
            "Choose this option if you want to be able to mark charges with "
            "an KLV/NV flag"
        )
    )

    def has_slots(self, weekday=0):
        if 0 <= weekday <= 6:
            return (len(self.available_slots[weekday]) > 0)
        else:
            return False

    def list_slots(self, weekday=0):
        if 0 <= weekday <= 6:
            return self.available_slots[weekday]
        else:
            return None

    class Meta:
        ordering = ('station', 'name')
        verbose_name = _("Dock")
        verbose_name_plural = _("Docks")
