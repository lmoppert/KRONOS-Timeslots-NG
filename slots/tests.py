from datetime import datetime
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
class StationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station = models.Station(company="KRONOS Leverkusen",
                                     name="TiO2 packed")
        cls.station.save()
        cls.dl = models.Deadline(name="Default")
        cls.dl.save()
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl)
        cls.dock.save()

    def test_station_creation(self):
        self.assertTrue(isinstance(self.station, models.Station))
        self.assertEqual(self.station.__str__(), "{} - {}".format(
            self.station.company, self.station.name))
        self.assertEqual(self.station.id, 1)
        self.assertEqual(self.station.get_absolute_url(),
                         '/{}'.format(self.station.id))

    def test_deadline_creation(self):
        self.assertTrue(isinstance(self.dl, models.Deadline))
        self.assertEqual(self.dl.__str__(), "{} ({} / {})".format(
            self.dl.name, self.dl.booking_deadline, self.dl.rnvp))

    def test_dock_creation(self):
        self.assertTrue(isinstance(self.dock, models.Dock))


class DockTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.station = models.Station(company="KRONOS Leverkusen",
                                     name="TiO2 packed")
        cls.dl = models.Deadline(name="Default")
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl, available_slots=myslots)

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


class SlotTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.now = datetime.strptime('2018-01-01', '%Y-%m-%d')
        cls.station = models.Station(company="KRONOS Leverkusen",
                                     name="TiO2 packed")
        cls.dl = models.Deadline(name="Default")
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl, available_slots=myslots)
        cls.slot = models.Slot(dock=cls.dock, date=cls.now, slot=1, line=0)

    def test_slot_creation(self):
        self.assertTrue(isinstance(self.slot, models.Slot))
        self.assertEqual(self.slot.__str__(), "Truck: 2018-01-01 8:00 (0)")


# Test views
class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station = models.Station(company="KRONOS Leverkusen",
                                     name="TiO2 packed")
        cls.station.save()
        cls.dl = models.Deadline(name="Default")
        cls.dl.save()
        myslots = [['7:00', '8:00', '9:00'], ['7:30'], [], [], [], [], []]
        cls.dock = models.Dock(name="Truck", station=cls.station,
                               deadline=cls.dl, available_slots=myslots)
        cls.dock.save()
        from django.test import Client
        cls.c = Client()

    def test_index(self):
        res = self.c.get('/')
        self.assertContains(res, 'Timeslots', 3)

    def test_station(self):
        res = self.c.get('/{}'.format(self.station.id))
        self.assertContains(res, 'KRONOS Leverkusen')
        self.assertContains(res, 'Truck')
        res = self.c.get('/{}/date/2018/1/2'.format(self.station.id))
        self.assertContains(res, '7:30')
