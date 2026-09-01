from django_filters import DateFilter
from django_filters.rest_framework import FilterSet

from apps.models import Transaction


class TransactionFilter(FilterSet):
    date_from = DateFilter(field_name='date', lookup_expr='gte')
    date_to = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['type', 'category', 'currency']