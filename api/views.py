import logging
from datetime import datetime

from django.http import FileResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from api.exceptions import InvoiceGenerationError, LanguageNotSupportedError
from api.models import Payer, Invoice
from api.permissions import IsOwner
from api.serializers import (PayerSerializer, InvoiceGenerationSerializer,
                             InvoiceFavoriteSerializer, InvoiceDisplaySerializer)
from api.utils.invoice_generator import InvoiceGenerator
import io


logger = logging.getLogger(__name__)


class PayerViewSet(ModelViewSet):
    """
    API endpoint that allows payers to be viewed or edited.

    retrieve: Return the given payer.
    list: Return a list of all the existing payers for the user.
    create: Create a new payer.
    update: Update a payer.
    destroy: Delete a payer.
    """
    serializer_class = PayerSerializer

    def get_permissions(self):
        """
        Get the permissions for the view.

        :return: List of permissions
        """
        if self.action == "create":
            return [IsAuthenticated()]
        else:
            return [IsOwner()]

    def get_queryset(self):
        """
        Get all the payers for the user.

        :return: Queryset of payers for the user
        """
        return Payer.objects.filter(owner=self.request.user)


class FavouritesViewSet(ModelViewSet):
    """
    API endpoint that allows favourite invoice templates to be
    viewed or edited.

    retrieve: Return the given favourite invoice template.
    list: Return a list of all the existing favourite invoice templates for the user.
    create: Create a new favourite invoice template.
    update: Update a favourite invoice template.
    destroy: Delete a favourite invoice template.
    """
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InvoiceFavoriteSerializer
        return InvoiceDisplaySerializer

    def get_queryset(self):
        """
        Get all the favourite invoice templates for the user.

        :return: Queryset of favourite invoice templates
        """
        return Invoice.objects.filter(receiver=self.request.user)


class GenerateInvoiceAPIView(APIView):
    """
    API endpoint that allows generating an invoice.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceDisplaySerializer

    def post(self, request):
        """
        Generate an invoice and return it as a PDF file.

        :param request: Request object.

        :return: Response object with a PDF file
        """
        serializer = InvoiceGenerationSerializer(data=request.data,
                                                 context={"request": request})

        if not serializer.is_valid():
            logger.warning("Invoice validation failed",
                           extra={"errors": serializer.errors})
            return Response({"error": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice_generator = InvoiceGenerator(serializer.validated_data,
                                                 request.user)
            pdf_bytes = invoice_generator.generate_invoice()

            if not pdf_bytes or isinstance(pdf_bytes, str):
                logger.error("Invalid PDF generated",
                             extra={"pdf_content": pdf_bytes})
                return Response(
                    {"error": "Failed to generate valid PDF"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            pdf_file = io.BytesIO(pdf_bytes)
            response = FileResponse(
                pdf_file,
                content_type="application/pdf",
                as_attachment=False
            )
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"invoice_{timestamp}.pdf"
            response["Content-Disposition"] = f'inline; filename="{filename}"'
            logger.info("Invoice generation successful")
            return response

        except InvoiceGenerationError as e:
            logger.exception("Invoice generation error")
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except LanguageNotSupportedError as e:
            logger.exception("Language not supported")
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error")
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
