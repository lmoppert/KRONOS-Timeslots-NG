from datetime import datetime, timedelta, timezone
from . import models


def remove_garbage():
    deadline = datetime.now(timezone.utc) - timedelta(minutes=5)
    for slot in models.Slot.drafts.filter(created__lte=deadline):
        slot.delete()
