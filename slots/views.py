from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views import generic
from slots import models


def index(request):
    context = {'objects': models.Station.objects.all()}
    return render(request, 'slots/index.html', context=context)


class StationRedirect(generic.RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        station = get_object_or_404(models.Station, pk=kwargs['pk'])
        today = datetime.today()
        if station.has_docks:
            return reverse('stationdocks',
                           kwargs={'year': today.year, 'month': today.month,
                                   'day': today.day, 'pk': station.pk})
        else:
            return reverse('index')


class StationDocks(LoginRequiredMixin, generic.DetailView):
    model = models.Station
    template_name = 'slots/station_detail.html'

    def get_dock_data(self, dock, date):
        starttimes = dock.available_slots[date.weekday()]
        reserved_slots = models.Slot.objects.filter(date=date, dock=dock)
        slots = []
        for i, start in enumerate(starttimes):
            slot = [start]
            for line in range(dock.linecount):
                qs = reserved_slots.filter(slot=i, line=line)
                if qs.exists():
                    obj = qs.first()
                    url = obj.get_absolute_url()
                    res = obj.user.usercompany
                    tag = mark_safe("<a href='{}'>{}</a>".format(url, res))
                else:
                    args = {'station': dock.station.pk, 'dock': dock.pk,
                            'line': line, 'year': date.year, 'day': date.day,
                            'month': date.month, }
                    url = reverse('dockslot', kwargs=args)
                    tag = mark_safe("<a href='{}' class='Free'>{}</a>".format(
                        url, _("Free")))
                slot += [tag]
            slots.append(slot)
        return slots

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.get_object()
        mydate = "{}-{}-{}".format(self.kwargs['year'], self.kwargs['month'],
                                   self.kwargs['day'])
        showdate = datetime.strptime(mydate, "%Y-%m-%d")
        docklist = []
        for dock in station.docks.all().order_by('pk'):
            docklist.append([dock.name, self.get_dock_data(dock, showdate)])
        context['docks'] = docklist
        context['showdate'] = showdate.date()  # .strftime("%A, %x")
        context['permission'] = station.get_user_role(self.request.user)
        return context


class DockSlot(generic.DetailView):
    model = models.Slot
    template_name = 'slots/slot_detail.html'
