from datetime import datetime, timedelta, timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views import generic
from . import models, forms


def _remove_garbage():
    deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
    for slot in models.Slot.drafts.filter(created__lte=deadline):
        slot.delete()


@login_required
def index(request):
    if request.user.is_superuser:
        objects = models.Station.objects.all()
    else:
        objects = models.Station.objects.filter(role__user=request.user)
    return render(request, 'slots/index.html', context={'objects': objects})


class StationRedirect(LoginRequiredMixin, generic.RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        _remove_garbage()
        station = get_object_or_404(models.Station, pk=kwargs['pk'])
        today = datetime.today()
        if station.has_docks:
            return reverse('stationdocks', kwargs={
                'year': today.year, 'month': today.month, 'day': today.day,
                'pk': station.pk})
        else:
            msg = _('Station "<em>{}</em>" has no docks assigned yet.').format(
                station)
            messages.warning(self.request, mark_safe(msg))
            return reverse('index')


class StationDocks(LoginRequiredMixin, generic.DetailView):
    model = models.Station
    template_name = 'slots/station_detail.html'

    def get_dock_data(self, dock, date):
        start_times = dock.available_slots[date.weekday()]
        reserved_slots = models.Slot.objects.filter(date=date, dock=dock)
        slots = []
        for i, start in enumerate(start_times):
            slot = [start]
            for line in range(dock.linecount):
                qs = reserved_slots.filter(index=i, line=line)
                if qs.exists():
                    obj = qs.first()
                    url = obj.get_absolute_url()
                    res = "{} - {}".format(obj.user.profile,
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
        _remove_garbage()
        station = self.get_object()
        if self.request.user.is_superuser:
            stations = models.Station.objects.all()
        else:
            stations = models.Station.objects.filter(
                role__user=self.request.user)
        showdate = datetime(
            year=self.kwargs['year'], month=self.kwargs['month'],
            day=self.kwargs['day']
        )
        docklist = []
        for dock in station.docks.all().order_by('pk'):
            docklist.append([dock.name, self.get_dock_data(dock, showdate)])
        context['docks'] = docklist
        context['stations'] = stations
        context['showdate'] = showdate.date()
        context['prevday'] = (showdate - timedelta(days=1)).day
        context['nextday'] = (showdate + timedelta(days=1)).day
        context['permission'] = station.get_user_role(self.request.user)
        return context


class SlotRedirect(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        _remove_garbage()
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        dock = self.object.dock
        if 'deleteSlot' in request.POST:
            self.object.delete()
            return HttpResponseRedirect(dock.station.get_absolute_url())
        if dock.multiple_charges:
            formset = forms.JobFormSet(request.POST, instance=self.object)
        else:
            formset = forms.SingleJobFormSet(request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('stationdocks', kwargs={
                'pk': self.object.dock.station.pk,
                'year': self.object.date.year,
                'month': self.object.date.month,
                'day': self.object.date.day,
            }))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.dock.multiple_charges:
            context['formset'] = forms.JobFormSet(instance=self.object)
            context['multiple_forms'] = True
        else:
            context['formset'] = forms.SingleJobFormSet(instance=self.object)
            context['multiple_forms'] = False
        return context
