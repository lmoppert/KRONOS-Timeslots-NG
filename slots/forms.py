from django.forms import inlineformset_factory
from .models import Slot, Job


JobFormSet = inlineformset_factory(
    Slot, Job, fields='__all__', min_num=1, extra=0, validate_min=True
)
SingleJobFormSet = inlineformset_factory(
    Slot, Job, fields='__all__', min_num=1, max_num=1, validate_min=True
)
