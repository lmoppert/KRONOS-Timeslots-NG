from datetime import datetime, timedelta, timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
            return reverse('stationdocks',
                           kwargs={'year': today.year, 'month': today.month,
                                   'day': today.day, 'pk': station.pk})
        else:
            msg = _('Station "<em>{}</em>" has no docks assigned yet.').format(
                station)
            messages.warning(self.request, mark_safe(msg))
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
        context['showdate'] = showdate.date()  # .strftime("%A, %x")
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


class SlotDisplay(generic.DetailView):
    model = models.Slot
    template_name = 'slots/slot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = forms.JobFormSet(instance=self.object)
        return context


class SlotJobs(generic.detail.SingleObjectMixin, generic.FormView):
    model = models.Slot
    template_name = 'slots/slot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = forms.JobFormSet(instance=self.object)
        return context


class SlotDetail(LoginRequiredMixin, generic.DetailView):
    """This view is using the above defined classes to provide the actual view.
    Which one to use is determined by the type of request we get (POST or GET).
    """
    def get(self, request, *args, **kwargs):
        view = SlotDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = SlotJobs.as_view()
        return view(request, *args, **kwargs)
