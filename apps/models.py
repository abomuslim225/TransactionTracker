from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import EmailField, Model, ForeignKey, CASCADE, Index, ImageField
from django.db.models.enums import TextChoices
from django.db.models.fields import CharField, DecimalField, DateTimeField, TextField


class User(AbstractUser):
    avatar = ImageField(upload_to="users/avatar/", blank=True, null=True)
    EMAIL_FIELD = "email"
    email = EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

class ExchangeRate(Model):
    class CurrencyChoice(TextChoices):
        USD = "USD", "AQSH dollari"
        EUR = "EUR", "Yevro"
    code = CharField(max_length=3, choices=CurrencyChoice, unique=True)
    rate_to_uzs = DecimalField(max_digits=14, decimal_places=4)
    updated_at = DateTimeField(auto_now=True)

class Category(Model):
    name = CharField(max_length=75, unique=True)

class Transaction(Model):
    class CurrencyChoice(TextChoices):
        UZS = "UZS", "So'm"
        USD = "USD", "AQSH dollari"
        EUR = "EUR", "Yevro"
    class TypeChoice(TextChoices):
        INCOME = "income", "kirim"
        EXPENSE = "expense", "chiqim"
    class StatusChoice(TextChoices):
        PENDING = "pending", "pending"
        CONFIRMED = "confirmed", "confirmed"
    user = ForeignKey("apps.User", on_delete=CASCADE, related_name="transactions")
    name = CharField(max_length=75)
    type = CharField(max_length=35, choices=TypeChoice)
    amount = DecimalField(max_digits=12, decimal_places=2)
    date = DateTimeField()
    currency = CharField(max_length=3, choices=CurrencyChoice, default=CurrencyChoice.UZS)
    description = TextField(blank=True, null=True)
    category = ForeignKey("apps.Category", on_delete=CASCADE)
    status = CharField(max_length=35, choices=StatusChoice)
    class Meta:
        indexes = [
            Index(fields=["user", "name"])
        ]
class Notification(Model):
    user = ForeignKey("apps.User", on_delete=CASCADE, related_name="notifications")
    transaction = ForeignKey("apps.Transaction", on_delete=CASCADE)

