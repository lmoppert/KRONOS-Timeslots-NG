from django.test import TestCase
from django.apps import apps
from slots.apps import SlotsConfig
from slots import models


# Test app
class SlotsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(SlotsConfig.name, 'slots')
        self.assertEqual(apps.get_app_config('slots').name, 'slots')


# Test models
class StationTests(TestCase):
    def test_station_creation(self):
        station = models.Station(company="KRONOS Leverkusen",
                                 name="TiO2 packed")
        self.assertTrue(isinstance(station, models.Station))
        self.assertEqual(station.__str__(), "{} - {}".format(station.company,
                                                             station.name))

    def test_deadline_creation(self):
        dl = models.Deadline(name="Default")
        self.assertTrue(isinstance(dl, models.Deadline))
        self.assertEqual(dl.__str__(), "{} ({} / {})".format(
            dl.name, dl.booking_deadline, dl.rnvp))

    def test_dock_creation(self):
        station = models.Station(company="KRONOS Leverkusen",
                                 name="TiO2 packed")
        dl = models.Deadline(name="Default")
        dock = models.Dock(name="Truck", station=station, deadline=dl)
        self.assertTrue(isinstance(dock, models.Dock))


# Test views
class ViewsTests(TestCase):
    def test_index(self):
        from django.test import Client
        c = Client()
        res = c.get('/')
        self.assertContains(res, 'Timeslots', 2)
