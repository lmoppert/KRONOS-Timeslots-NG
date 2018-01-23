from datetime import datetime, time, timezone, timedelta
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.db.models import F
from django.urls import reverse
from django.db import models


class Deadline(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    booking_deadline = models.TimeField(
        default='00:00:00', verbose_name=_("Booking Deadline"),
        help_text=_("Booking deadline = time on the day before from which on a "
                    "slot can not be reserved any more. Set this to midnight "
                    "to turn off this feature completely for this station"))
    rnvp = models.TimeField(
        default='00:00:00', verbose_name=_("Edit Deadline"),
        help_text=_("RVNP = Rien ne vas plus -- time when a slot can not be "
                    "edited any more, set to Midnight to have the deadline as "
                    "RNVP"))

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
    location = models.CharField(max_length=200, verbose_name=_("Location"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    def get_user_role(self, user):
        qs = self.role_set.filter(user__id=user.id)
        if qs.exists():
            return qs.first().role
        else:
            return 0

    @property
    def has_docks(self):
        return self.docks.all().exists()

    # @property
    # def has_silos(self):
    #     return self.silos.all().exists()

    def __str__(self):
        return "{} - {}".format(self.location, self.name)

    def get_absolute_url(self):
        return reverse('station', args=[str(self.id)])

    class Meta:
        verbose_name = _("Station")
        verbose_name_plural = _("Stations")


class Dock(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    station = models.ForeignKey(Station, on_delete=models.CASCADE,
                                related_name='docks', verbose_name=_("Station"))
    linecount = models.PositiveSmallIntegerField(default=1,
                                                 verbose_name=_("Line Count"))
    slotlength = models.PositiveSmallIntegerField(default=60,
                                                  verbose_name=_("Slot Legth"))
    max_slots = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Max Slots"), help_text=_("0 for unlimited"))
    available_slots = JSONField(default=[[], [], [], [], [], [], []],
                                verbose_name=_("Available Slots"))
    deadline = models.ForeignKey(Deadline, default=1, on_delete=models.CASCADE,
                                 verbose_name=_("Deadline"))
    multiple_charges = models.BooleanField(
        default=True, verbose_name=_("Multiple Charges"),
        help_text=_("If this option is marked, the reservation form offers the "
                    "opportunity to add more than one job"))
    has_status = models.BooleanField(
        default=False, verbose_name=_("Has Status"),
        help_text=_("This option adds a Statusbar to the job view, which shows "
                    "the current loading status"))
    has_klv = models.BooleanField(
        default=False, verbose_name=_("Has KLV"),
        help_text=_("Choose this option if you want to be able to mark charges "
                    "with an KLV/NV flag"))

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

    def __str__(self):
        return "{} - {}".format(self.station, self.name)

    class Meta:
        ordering = ('station', 'name')
        verbose_name = _("Dock")
        verbose_name_plural = _("Docks")


class Slot(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, default=1,
                             verbose_name=_("User"))
    dock = models.ForeignKey(Dock, on_delete=models.CASCADE,
                             verbose_name=_("Dock"))
    date = models.DateField(auto_now=False, verbose_name=_("Date"))
    index = models.IntegerField(verbose_name=_("Index"))
    line = models.IntegerField(verbose_name=_("Line"))
    progress = models.PositiveSmallIntegerField(default=0,
                                                verbose_name=_("Progress"))
    is_klv = models.BooleanField(default=False, verbose_name=_("Is KLV"))
    is_blocked = models.BooleanField(default=False,
                                     verbose_name=_("Is Blocked"))
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name=_("Time Created"))

    @property
    def age(self):
        """calculate the age of this slot in minutes"""
        td = datetime.now(timezone.utc) - self.created
        return int(divmod(td.total_seconds(), 60)[0])

    @property
    def has_jobs(self):
        return (self.job_set.all().count() >= 1)

    @property
    def start(self):
        start = self.dock.available_slots[self.date.weekday()][self.index]
        hour, minute = start.split(":")
        starttime = time(hour=int(hour), minute=int(minute))
        return starttime

    @property
    def end(self):
        start = datetime.combine(datetime.today(), self.start)
        end = start + timedelta(minutes=self.dock.slotlength)
        return end.time()

    def get_absolute_url(self):
        return reverse('slotdetail', args=[str(self.pk)])

    def __str__(self):
        start = self.dock.available_slots[self.date.weekday()][self.index]
        mydate = self.date.strftime("%Y-%m-%d")
        return "{}: {} {} ({})".format(self.dock.name, mydate, start, self.line)

    class Meta:
        ordering = ('dock', F('date').asc(), 'index', 'line')
        verbose_name = _("Timelot")
        verbose_name_plural = _("Timeslots")


class Job(models.Model):
    PAYLOADS = [(x + 1, "{} t".format(x+1)) for x in range(40)]
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE,
                             verbose_name=_("Slot"))
    number = models.CharField(max_length=25, verbose_name=_("Order Number"))
    payload = models.PositiveSmallIntegerField(default=25, choices=PAYLOADS,
                                               verbose_name=_("Payload"))
    description = models.CharField(max_length=200, blank=True,
                                   verbose_name=_("Description"))

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")


class Company(models.Model):
    shortname = models.CharField(max_length=20, blank=True,
                                 verbose_name=_("Short Name"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    contact = models.TextField(blank=True, verbose_name=_("Contact"))

    def __str__(self):
        if len(self.shortname) > 1:
            return "{} ({})".format(self.name, self.shortname)
        else:
            return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


class UserCompany(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                verbose_name=_("User"))
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                verbose_name=_("Company"))

    def __str__(self):
        if len(self.company.shortname) > 1:
            return self.company.shortname
        else:
            return self.company.name

    class Meta:
        verbose_name = _("User Company")
        verbose_name_plural = _("User Companies")


class Role(models.Model):
    ROLES = ((1, _("carrier")), (2, _("viewer")), (3, _("charger")),
             (4, _("loadmaster")))
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(choices=ROLES, default=2)

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        unique_together = ("user", "station")


# class Silo(models.Model):
#     name = models.CharField(max_length=200, verbose_name=_("Name"))
#     station = models.ForeignKey(Station, on_delete=models.CASCADE,
#                                 related_name='silos')
