from django.contrib import admin
from .models import Invoice, Payer, Purpose


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    list_display = ["name_ka", "name_en", "id", "owner__email"]
    search_fields = ["name_ka", "name_en", "id"]
    list_filter = ["owner__email"]
    list_select_related = ["owner"]


@admin.register(Purpose)
class PurposeAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "has_vat", "vat_amount",
                    "invoice__invoice_number"]
    search_fields = ["description"]
    list_filter = ["has_vat"]
    list_select_related = ["invoice"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["receiver__email", "payer__name_ka", "total_amount",
                    "invoice_number"]
    search_fields = ["receiver__email", "payer__name_ka", "invoice_number"]
    list_select_related = ["receiver", "payer"]


