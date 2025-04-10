from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Payer, Purpose, Invoice
from api.utils.invoice_generator import InvoiceNumberGenerator


class PayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payer
        exclude = ["owner"]

    def validate(self, attrs):
        # Add an owner to validated data
        attrs["owner"] = self.context["request"].user
        return attrs


class PurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purpose
        fields = "__all__"


class InvoiceGenerationSerializer(ModelSerializer):
    purposes = PurposeSerializer(many=True)  # Nested serializer

    class Meta:
        model = Invoice
        exclude = ["name"]
        read_only_fields = ['receiver', 'total_amount', 'invoice_number']

    def validate(self, attrs):
        language = attrs.get("language")
        template = attrs.get("template")
        if language and language not in ["en", "ka"]:
            raise serializers.ValidationError(f"Language should be one "
                                              f"of ['en', 'ka']")

        if template and template not in ["template1",
                                         "template2",
                                         "template3",
                                         "template4"]:
            raise serializers.ValidationError(
                f"Template should be one of "
                f"['template1', 'template2', 'template3', 'template4']"
            )
        return attrs


class InvoiceFavoriteSerializer(ModelSerializer):
    purposes = PurposeSerializer(many=True)  # Nested serializer

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ['receiver', 'total_amount', 'invoice_number']

    def validate(self, attrs):
        language = attrs.get("language")
        template = attrs.get("template")
        if language and language not in ["en", "ka"]:
            raise serializers.ValidationError(f"Language should be one "
                                              f"of ['en', 'ka']")

        if template and template not in ["template1",
                                         "template2",
                                         "template3",
                                         "template4"]:
            raise serializers.ValidationError(
                f"Template should be one of "
                f"['template1', 'template2', 'template3', 'template4']"
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Count vat amounts and total amount of the receipt.

        :param validated_data: Data to be validated

        :return: Created invoice
        """
        purposes = validated_data.pop("purposes")
        payer = validated_data.pop("payer")
        invoice_number = InvoiceNumberGenerator().generate()

        validated_data['invoice_number'] = invoice_number

        invoice = Invoice.objects.create(
            receiver=self.context["request"].user,
            payer=payer,
            **validated_data
        )
        # Bulk create purposes
        purposes_list = [Purpose(
            invoice=invoice, **purpose
        ) for purpose in purposes]
        Purpose.objects.bulk_create(purposes_list)
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update invoice instance.

        :param instance: Invoice instance
        :param validated_data: Validated data

        :return: updated invoice.
        """
        purposes_data = validated_data.pop('purposes', None)
        payer = validated_data.pop('payer', instance.payer)
        invoice_number = InvoiceNumberGenerator().generate()
        validated_data['invoice_number'] = invoice_number

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.payer = payer

        if purposes_data is not None:
            instance.purposes.all().delete()
            purposes_list = [Purpose(
                invoice=instance, **purpose
            ) for purpose in purposes_data]
            Purpose.objects.bulk_create(purposes_list)
        instance.save()
        return instance


class InvoiceDisplaySerializer(ModelSerializer):
    purposes = PurposeSerializer(many=True)
    payer = PayerSerializer()

    class Meta:
        model = Invoice
        fields = "__all__"
        read_only_fields = ['receiver', 'total_amount', 'invoice_number']

    def validate(self, attrs):
        language = attrs.get("language")
        template = attrs.get("template")
        if language and language not in ["en", "ka"]:
            raise serializers.ValidationError(f"Language should be one "
                                              f"of ['en', 'ka']")

        if template and template not in ["template1",
                                         "template2",
                                         "template3",
                                         "template4"]:
            raise serializers.ValidationError(
                f"Template should be one of "
                f"['template1', 'template2', 'template3', 'template4']"
            )
        return attrs
