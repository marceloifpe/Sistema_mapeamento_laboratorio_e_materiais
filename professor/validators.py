from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def validate_date_not_past(date):
    if date < timezone.now():
        raise ValidationError(
            _('%(date)s is in the past'),
            params={'date': date},
        )
