from datetime import datetime, timedelta
from django.test import TestCase
from django.apps import apps
from slots.apps import SlotsConfig
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
        cls.dl = models.Deadline(name="Default")
        cls.dl.save()
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl, available_slots=myslots)
        cls.dock.save()
        mydate = datetime.strptime('2018-01-01', '%Y-%m-%d')
        cls.tgl = models.Company(name="KRONOS LEV", shortname="TGL")
        cls.tgl.save()
        cls.company = models.Company(name="MyCompany")
        cls.company.save()
        cls.carrier = models.User(username='carrier', password='pass')
        cls.carrier.save()
        models.UserCompany(user=cls.carrier, company=cls.company).save()
        cls.master = models.User(username='master', password='pass')
        cls.master.save()
        models.UserCompany(user=cls.master, company=cls.tgl).save()
        cls.dummy = models.User(username='dummy', password='pass')
        cls.dummy.save()
        models.UserCompany(user=cls.dummy, company=cls.company).save()
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

    def test_deadline_creation(self):
        self.assertTrue(isinstance(self.dl, models.Deadline))
        self.assertEqual(self.dl.__str__(), "{} ({} / {})".format(
            self.dl.name, self.dl.booking_deadline, self.dl.rnvp))

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

    def test_slot_age(self):
        self.slot.created -= timedelta(minutes=10)
        self.assertEqual(self.slot.age, 10)

    def test_slot_has_jobs(self):
        self.assertTrue(self.slot.has_jobs)
        newslot = models.Slot(dock=self.dock, date=self.slot.date, index=0,
                              line=0, user=self.carrier)
        self.assertFalse(newslot.has_jobs)

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
        self.assertEqual(self.tgl.usercompany_set.first().__str__(), "TGL")

    # User access tests
    def test_carrier(self):
        self.assertTrue(isinstance(self.carrier, models.User))
        self.assertEqual(self.station.get_user_role(self.carrier), 1)

    def test_master(self):
        self.assertTrue(isinstance(self.carrier, models.User))
        self.assertEqual(self.station.get_user_role(self.master), 4)

    def test_dummy(self):
        self.assertTrue(isinstance(self.carrier, models.User))
        self.assertEqual(self.station.get_user_role(self.dummy), 0)


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
        cls.dl = models.Deadline(name="Default")
        cls.dl.save()
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl, available_slots=myslots)
        cls.dock.save()
        cls.today = datetime.today()
        cls.company = models.Company(name="MyCompany")
        cls.company.save()
        cls.carrier = models.User(username='carrier')
        cls.carrier.set_password("cpass")
        cls.carrier.save()
        models.UserCompany(user=cls.carrier, company=cls.company).save()
        cls.master = models.User(username='master')
        cls.master.set_password("mpass")
        cls.master.save()
        models.UserCompany(user=cls.master, company=cls.company).save()
        cls.dummy = models.User(username='dummy')
        cls.dummy.set_password("dpass")
        cls.dummy.save()
        models.UserCompany(user=cls.dummy, company=cls.company).save()
        cls.slotdate = datetime.strptime('2018-01-01', '%Y-%m-%d')
        cls.slot = models.Slot(dock=cls.dock, date=cls.slotdate, index=1,
                               line=0, user=cls.carrier)
        cls.slot.save()
        cls.job = models.Job(number="4711", slot=cls.slot)
        cls.job.save()

    def test_index(self):
        res = self.c.get('/')
        self.assertContains(res, 'Timeslots', 3)

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
