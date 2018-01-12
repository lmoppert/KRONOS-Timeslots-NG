from datetime import datetime
from django.shortcuts import render
from django.views import generic
from slots import models


def index(request):
    context = {'objects': models.Station.objects.all()}
    return render(request, 'slots/index.html', context=context)


class StationDetail(generic.DeleteView):
    model = models.Station
    template_name = 'slots/station_detail.html'

    def get_dock_data(self, dock, date):
        starttimes = dock.available_slots[date.weekday()]
        reserved_slots = models.Slot.objects.filter(date=date, dock=dock)
        slots = []
        for i, start in enumerate(starttimes):
            slot = [start]
            for line in range(dock.linecount):
                try:
                    tag = str(reserved_slots.get(slot=i, line=line))
                except:
                    tag = "FREE"
                slot += [tag]
            slots.append(slot)
        return slots

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.get_object()
        if 'year' in self.kwargs:
            mydate = "{}-{}-{}".format(self.kwargs['year'],
                                       self.kwargs['month'], self.kwargs['day'])
            showdate = datetime.strptime(mydate, "%Y-%m-%d")
        else:
            showdate = datetime.today()
        docklist = {}
        for dock in station.docks.all():
            docklist[dock.name] = self.get_dock_data(dock, showdate)
        context['docks'] = docklist
        context['showdate'] = showdate.strftime("%A, %x")
        return context
