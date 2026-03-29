from django.db import models
from django.utils.translation import gettext_lazy as _


class IngestRawStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    VALID = "valid", _("Valid")
    INVALID = "invalid", _("Invalid")
    SUCCESS = "success", _("Success")
