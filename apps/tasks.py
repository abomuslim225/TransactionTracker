import requests
from celery import shared_task

from apps.models import ExchangeRate

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


@shared_task
def update_exchange_rates():

    response = requests.get(CBU_URL, params={"vid_currency": ["USD", "EUR"]}, timeout=15)
    response.raise_for_status()
    data = response.json()

    for row in data:
        code = row.get("Ccy")
        if code not in ("USD", "EUR"):
            continue
        ExchangeRate.objects.update_or_create(
            code=code,
            defaults={"rate_to_uzs": row.get("Rate")},
        )