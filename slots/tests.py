from datetime import datetime, timedelta, time, timezone
from django.test import TestCase
from django.apps import apps
from slots.apps import SlotsConfig
from slots.views import _remove_garbage
from slots import models


# Test basics
class SlotsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(SlotsConfig.name, 'slots')
        self.assertEqual(apps.get_app_config('slots').name, 'slots')


class HelperScriptsTest(TestCase):
    def test_generate_slots(self):
        from scripts.helper import generate_slots

        slotlist = ['07:00', '07:45', '08:30', '09:15', '10:00']
        self.assertEquals(generate_slots('7:00', 45, 5), slotlist)


# Test models
class ModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station = models.Station(location="Leverkusen", name="packed")
        cls.station.save()
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.dock = models.Dock(name="Truck", station=cls.station, slotlength=60,
                               available_slots=myslots)
        cls.dock.save()
        mydate = datetime.strptime('2018-01-01', '%Y-%m-%d')
        cls.tgl = models.Company(name="KRONOS LEV", shortname="TGL")
        cls.tgl.save()
        cls.company = models.Company(name="MyCompany")
        cls.company.save()
        cls.carrier = models.User(username='carrier', password='pass')
        cls.carrier.save()
        models.Profile(user=cls.carrier, company=cls.company).save()
        cls.master = models.User(username='master', password='pass',
                                 first_name="Load", last_name="Master")
        cls.master.save()
        models.Profile(user=cls.master, company=cls.tgl).save()
        cls.dummy = models.User(username='dummy', password='pass')
        cls.dummy.save()
        models.Profile(user=cls.dummy, company=cls.company).save()
        cls.slot = models.Slot(dock=cls.dock, date=mydate, index=1, line=0,
                               user=cls.carrier)
        cls.slot.save()
        cls.job = models.Job(number="4711", slot=cls.slot)
        cls.job.save()
        models.Role(station=cls.station, user=cls.carrier, role=1).save()
        models.Role(station=cls.station, user=cls.master, role=4).save()

    # Station tests
    def test_station_creation(self):
        self.assertTrue(isinstance(self.station, models.Station))
        self.assertEqual(self.station.__str__(), "{} - {}".format(
            self.station.location, self.station.name))
        self.assertEqual(self.station.pk, 1)

    def test_station_ablosute_url(self):
        self.assertEqual(self.station.get_absolute_url(),
                         '/{}'.format(self.station.pk))

    # Dock tests
    def test_dock_creation(self):
        self.assertTrue(isinstance(self.dock, models.Dock))
        self.assertEqual(self.dock.__str__(), "{} - {}".format(
            self.station, self.dock.name))

    def test_dock_slot_flag(self):
        self.assertTrue(self.dock.has_slots(1))
        self.assertFalse(self.dock.has_slots(2))
        self.assertFalse(self.dock.has_slots(9))

    def test_dock_slot_list(self):
        self.assertEqual(self.dock.list_slots(1), ['7:30'])
        self.assertEqual(self.dock.list_slots(2), [])
        self.assertEqual(self.dock.list_slots(9), None)

    # Slot tests
    def test_slot_creation(self):
        self.assertTrue(isinstance(self.slot, models.Slot))
        self.assertEqual(self.slot.__str__(), "Truck: 2018-01-01 8:00 (0)")

    def test_slot_ablosute_url(self):
        self.assertEqual(self.slot.get_absolute_url(),
                         '/slot/{}'.format(self.slot.pk))

    def test_garbage_collector(self):
        mydate = datetime.strptime('2018-01-01', '%Y-%m-%d')
        slot = models.Slot(user=self.carrier, dock=self.dock, date=mydate,
                           index=1, line=1)
        slot.save()
        self.assertEqual(models.Slot.objects.count(), 2)
        _remove_garbage()
        self.assertEqual(models.Slot.objects.count(), 2)
        slot.created = datetime.now(timezone.utc)-timedelta(minutes=10)
        slot.save()
        _remove_garbage()
        self.assertEqual(models.Slot.objects.count(), 1)

    def test_slot_manager(self):
        self.assertEqual(models.Slot.objects.count(), 1)
        self.assertEqual(models.Slot.drafts.count(), 0)
        self.assertEqual(models.Slot.reservations.count(), 1)
        self.assertEqual(models.Slot.blockings.count(), 0)
        newslot = models.Slot(dock=self.dock, date=self.slot.date, index=0,
                              line=0, user=self.carrier)
        newslot.save()
        self.assertEqual(models.Slot.objects.count(), 2)
        self.assertEqual(models.Slot.drafts.count(), 1)
        self.assertEqual(models.Slot.reservations.count(), 1)
        self.assertEqual(models.Slot.blockings.count(), 0)
        newslot.is_blocked = True
        newslot.save()
        self.assertEqual(models.Slot.objects.count(), 2)
        self.assertEqual(models.Slot.drafts.count(), 0)
        self.assertEqual(models.Slot.reservations.count(), 1)
        self.assertEqual(models.Slot.blockings.count(), 1)

    def test_slot_times(self):
        self.assertEqual(self.slot.start, time(hour=8))
        self.assertEqual(self.slot.end, time(hour=9))

    # Job tests
    def test_job_creation(self):
        self.assertTrue(isinstance(self.job, models.Job))
        self.assertEqual(self.job.__str__(), "4711")

    # Company tests
    def test_company_creation(self):
        self.assertTrue(isinstance(self.company, models.Company))
        self.assertEqual(self.company.__str__(), "MyCompany")

    def test_company_names(self):
        self.assertEqual(self.tgl.__str__(), "KRONOS LEV (TGL)")
        self.assertEqual(self.tgl.profile_set.first().__str__(), "TGL")

    # User access tests
    def test_carrier(self):
        self.assertTrue(isinstance(self.carrier, models.User))
        self.assertEqual(self.station.get_user_role(self.carrier), 1)

    def test_master(self):
        self.assertTrue(isinstance(self.master, models.User))
        self.assertEqual(self.station.get_user_role(self.master), 4)

    def test_dummy(self):
        self.assertTrue(isinstance(self.dummy, models.User))
        self.assertEqual(self.station.get_user_role(self.dummy), 0)
        self.assertEqual(len(self.dummy.profile.get_stations()), 0)

    def test_super_dummy(self):
        self.dummy.is_superuser = True
        self.dummy.save()
        self.assertEqual(self.station.get_user_role(self.dummy), 4)
        self.assertEqual(len(self.dummy.profile.get_stations()), 1)
        self.dummy.is_superuser = False
        self.dummy.save()


# Test views
class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.test import Client

        cls.c = Client()
        cls.empty = models.Station(location="Empty", name="Station")
        cls.empty.save()
        cls.station = models.Station(location="Leverkusen", name="packed")
        cls.station.save()
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.dock = models.Dock(name="Truck", station=cls.station, slotlength=60,
                               available_slots=myslots)
        cls.dock.save()
        cls.today = datetime.today()
        cls.company = models.Company(name="MyCompany")
        cls.company.save()
        cls.carrier = models.User(username='carrier')
        cls.carrier.set_password("cpass")
        cls.carrier.save()
        models.Profile(user=cls.carrier, company=cls.company).save()
        cls.master = models.User(username='master')
        cls.master.set_password("mpass")
        cls.master.save()
        models.Profile(user=cls.master, company=cls.company).save()
        cls.dummy = models.User(username='dummy')
        cls.dummy.set_password("dpass")
        cls.dummy.save()
        models.Profile(user=cls.dummy, company=cls.company).save()
        cls.slotdate = datetime.strptime('2018-01-01', '%Y-%m-%d')
        cls.slot = models.Slot(dock=cls.dock, date=cls.slotdate, index=1,
                               line=0, user=cls.carrier)
        cls.slot.save()
        cls.job = models.Job(number="4711", slot=cls.slot)
        cls.job.save()

    def test_show_role_tag(self):
        from slots.templatetags.slot_tags import show_role
        self.assertEqual(show_role(1), " ({})".format(models.Role.ROLES[0][1]))

    def test_index(self):
        res = self.c.get('/')
        self.assertRedirects(res, '/accounts/login/?next=/')
        self.dummy.is_superuser = True
        self.dummy.save()
        self.c.login(username='dummy', password='dpass')
        res = self.c.get('/')
        self.assertContains(res, 'Leverkusen - packed')
        self.dummy.is_superuser = False
        self.dummy.save()

    def test_auth_redirect(self):
        url = '/docks/{}/date/2018/1/2'.format(self.station.pk)
        res = self.c.get(url)
        self.assertRedirects(res, '/accounts/login/?next={}'.format(url))
        self.assertTrue(self.c.login(username='master', password='mpass'))

    def test_station_redirects(self):
        self.c.login(username='master', password='mpass')
        res = self.c.get('/{}'.format(self.station.pk))
        self.assertRedirects(res, '/docks/{}/date/{}/{}/{}'.format(
            self.station.pk, self.today.year, self.today.month, self.today.day))
        res = self.c.get('/{}'.format(self.empty.pk))
        self.assertRedirects(res, '/')

    def test_station_by_date(self):
        self.c.login(username='master', password='mpass')
        res = self.c.get('/docks/{}/date/2018/1/2'.format(self.station.pk))
        self.assertContains(res, '7:30')

    def test_station_by_date_as_superuser(self):
        self.dummy.is_superuser = True
        self.dummy.save()
        self.c.login(username='dummy', password='dpass')
        res = self.c.get('/docks/{}/date/2018/1/2'.format(self.station.pk))
        self.assertContains(res, '7:30')
        self.dummy.is_superuser = False
        self.dummy.save()

    def test_slot_in_table(self):
        self.c.login(username='master', password='mpass')
        res = self.c.get('/docks/{}/date/2018/1/1'.format(self.station.pk))
        self.assertContains(res, 'MyCompany - 4711')

    def test_slot_redirect(self):
        self.c.login(username='carrier', password='cpass')
        url = '/slot/{}/{}/{}/date/{}'.format(
            self.slot.dock.pk, self.slot.index, self.slot.line,
            self.slotdate.strftime('%Y/%m/%d'))
        res = self.c.get(url)
        self.assertRedirects(res, '/slot/{}'.format(self.slot.pk))

    def test_slot_redirect_new(self):
        before_count = len(models.Slot.objects.all())
        self.c.login(username='carrier', password='cpass')
        url = '/slot/{}/0/0/date/2018/1/9'.format(self.slot.dock.pk)
        res = self.c.get(url)
        self.assertEqual(len(models.Slot.objects.all()), before_count + 1)
        slot = models.Slot.objects.last()
        self.assertRedirects(res, '/newslot/{}'.format(slot.pk))
        self.assertEqual(slot.user.username, 'carrier')

# Not implemented yet
#    def test_slot_form(self):
#        self.c.login(username='carrier', password='cpass')
#        url = '/slot/{}'.format(self.slot.pk)
#        res = self.c.post(url, {
#            'job_set-0-number': '4711', 'job_set-0-payload': '25'})
#        self.assertContains(res, 'Reservation for')
