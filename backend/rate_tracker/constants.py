from django.db import models
from django.utils.translation import gettext_lazy as _


class IngestRawStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    VALIDATED = 'validated', _('Validated')
    PERSISTED = 'persisted', _('Persisted')
    FAILED = 'failed', _('Failed')
    REMOVE = 'remove', _('Remove')
