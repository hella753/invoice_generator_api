from django.db import models
from api.choices import CURRENCIES
from user.models import User


class Payer(models.Model):
    id = models.AutoField(primary_key=True)
    identification_code = models.CharField(max_length=100)
    name_ka = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey("user.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.name_ka


class Purpose(models.Model):
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    has_vat = models.BooleanField(default=False)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    invoice = models.ForeignKey("Invoice",
                                on_delete=models.CASCADE,
                                related_name="purposes",
                                blank=True,
                                null=True)

    def __str__(self):
        return self.description


class Invoice(models.Model):
    name = models.CharField(max_length=100)
    receiver = models.ForeignKey("user.User",
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    payer = models.ForeignKey("Payer", on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(choices=CURRENCIES, max_length=4)
    language = models.CharField(max_length=2, default="ka")
    should_use_invoice_date_currency_rate = models.BooleanField(default=False)
    template = models.CharField(max_length=100, default="template1")

    def __str__(self):
        return self.invoice_number