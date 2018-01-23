from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views import generic
from slots import models


@login_required
def index(request):
    context = {'objects': models.Station.objects.all()}
    return render(request, 'slots/index.html', context=context)


class StationRedirect(LoginRequiredMixin, generic.RedirectView):
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
                qs = reserved_slots.filter(index=i, line=line)
                if qs.exists():
                    obj = qs.first()
                    url = obj.get_absolute_url()
                    res = "{} - {}".format(obj.user.usercompany,
                                           obj.job_set.first())
                    anchor = "<a href='{}' class='text-info'>{}</a>"
                    tag = mark_safe(anchor.format(url, res))
                else:
                    args = {'dock': dock.pk, 'index': i, 'line': line,
                            'year': date.year, 'month': date.month,
                            'day': date.day}
                    url = reverse('getslot', kwargs=args)
                    anchor = "<a href='{}' class='text-success'>{}</a>"
                    tag = mark_safe(anchor.format(url, _("Free")))
                slot += [tag]
            slots.append(slot)
        return slots

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        station = self.get_object()
        showdate = datetime(
            year=self.kwargs['year'], month=self.kwargs['month'],
            day=self.kwargs['day']
        )
        docklist = []
        for dock in station.docks.all().order_by('pk'):
            docklist.append([dock.name, self.get_dock_data(dock, showdate)])
        context['docks'] = docklist
        context['showdate'] = showdate.date()  # .strftime("%A, %x")
        context['permission'] = station.get_user_role(self.request.user)
        return context


class SlotRedirect(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slotdate = datetime(
            year=kwargs['year'], month=kwargs['month'], day=kwargs['day']
        )
        dock = get_object_or_404(models.Dock, pk=kwargs['dock'])
        slot, created = models.Slot.objects.get_or_create(
            dock=dock, date=slotdate, index=kwargs['index'],
            line=kwargs['line'])
        if created:
            slot.user = self.request.user
            slot.save()
            return reverse('newslot', kwargs={'pk': slot.pk})
        else:
            return reverse('slotdetail', kwargs={'pk': slot.pk})


class SlotDetail(LoginRequiredMixin, generic.DetailView):
    model = models.Slot
    template_name = 'slots/slot_detail.html'
