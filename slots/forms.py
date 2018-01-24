from django.forms import inlineformset_factory
from . import models


JobFormSet = inlineformset_factory(
    models.Slot, models.Job, fields='__all__', extra=1)
