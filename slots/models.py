from datetime import timedelta, datetime, time
from django.db import models


class Configuration(models.Model):
    linecount = models.IntegerField()
    max_slots = models.IntegerField(default=0, help_text=_("0 for unlimited"))
    booking_deadline = models.TimeField(
        help_text=_(
            "Booking deadline = time on the day before from which on a slot "
            "can not be reserved any more. Set this to midnight to turn off "
            "this feature completely for this station"
        )
    )
    rnvp = models.TimeField(
        help_text=_(
            "RVNP = Rien ne vas plus -- time when a slot can not be edited "
            "any more, set to Midnight to have the deadline as RNVP"
        )
    )
    opened_on_weekend = models.BooleanField(
        default=False,
        help_text=_(
            "Choose this option if this station will be opened on weekends"
        )
    )
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

    def past_deadline(self, curr_date, curr_time):
        my_dl = self.booking_deadline
        if my_dl == time(0, 0):
            deadline = datetime.combine(curr_date + timedelta(days=1), my_dl)
        else:
            deadline = datetime.combine(curr_date - timedelta(days=1), my_dl)
        return curr_time > deadline

    class Meta:
        verbose_name = _("Configuration")
        verbose_name_plural = _("Configurations")


class Station(models.Model):
    company = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    configuration = models.ForeignKey(Configuration, on_delete=models.PROTECT)

    def __str__(self):
        return "{} - {}".format(self.company, self.name)

    class Meta:
        verbose_name = _("Station")
        verbose_name_plural = _("Stations")


class Dock(models.Model):
    name = models.CharField(max_length=200)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    configuration = models.ForeignKey(Configuration, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Dock")
        verbose_name_plural = _("Docks")
