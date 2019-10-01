import django_filters
from .models import Campaign

class CampaignFilter(django_filters.FilterSet):
    class Meta:
        model=Campaign
