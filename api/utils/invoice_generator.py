import datetime
import logging
from decimal import Decimal
from enum import Enum
from typing import Union, Any, Dict, Tuple, Optional
from django.template.loader import get_template
from dotenv import load_dotenv
from weasyprint import HTML
from api.exceptions import InvoiceGenerationError, LanguageNotSupportedError
from api.utils.months import MONTHS_IN_GEORGIAN, MONTHS_IN_ENGLISH
from user.models import User


load_dotenv()
logger = logging.getLogger(__name__)


class Language(str, Enum):
    """
    Supported languages for invoice generation.
    """
    ENGLISH = "en"
    GEORGIAN = "ka"


class TemplateType(str, Enum):
    """
    Available invoice template types.
    """
    TEMPLATE1 = "template1"
    TEMPLATE2 = "template2"
    TEMPLATE3 = "template3"
    TEMPLATE4 = "template4"


class VATCalculator:
    """
    Responsible for VAT-related calculations.
    """

    VAT_RATE = Decimal("0.18")

    @classmethod
    def calculate_vat_amount(cls, amount: Decimal, has_vat: bool) -> Decimal:
        """
        Calculate VAT amount based on the amount and VAT flag.

        :param: amount: Base amount for VAT calculation
        :param: has_vat: Flag indicating if VAT should be applied

        :return: Decimal: Calculated VAT amount (0 if it has_vat is False)
        """
        return amount * cls.VAT_RATE if has_vat else Decimal("0.00")


class InvoiceNumberGenerator:
    """
    Responsible for generating unique invoice numbers.
    """
    
    @staticmethod
    def generate() -> str:
        """
        Generate a unique invoice number based on current timestamp.

        :return: str: Formatted invoice number (YYYYDDMMHHMMSS)
        """
        return datetime.datetime.now().strftime("%Y%d%m%H%M%S")


class InvoiceService:
    """
    Service class for invoice generation helper methods
    to calculate VAT amount, generate invoice number and
    calculate total amount of the invoice.
    """

    @staticmethod
    def calculate_totals(data: Dict[str, Any]) -> Tuple[Decimal, Decimal]:
        """
        Calculate the total amount and total VAT of the invoice.

        :param: data: Invoice data containing purposes

        :return: Tuple[Decimal, Decimal]: (total_amount, vat_total)
        """
        if not data or "purposes" not in data:
            return Decimal("0.00"), Decimal("0.00")

        total_amount = Decimal("0.00")
        vat_total = Decimal("0.00")

        for purpose in data["purposes"]:
            amount = Decimal(str(purpose["amount"]))
            has_vat = bool(purpose["has_vat"])
            vat_amount = VATCalculator.calculate_vat_amount(amount, has_vat)

            purpose['vat_amount'] = round(vat_amount, 2)
            purpose['total'] = round(amount + vat_amount, 2)

            total_amount += (amount + vat_amount)
            vat_total += vat_amount

        return round(total_amount, 2), round(vat_total, 2)


class TemplateSelector:
    """
    Handles template selection based on language and template type.
    """

    TEMPLATE_MAPPING = {
        Language.ENGLISH: {
            TemplateType.TEMPLATE1: "invoice_template_1_en.html",
            TemplateType.TEMPLATE2: "invoice_template_2_en.html",
            TemplateType.TEMPLATE3: "invoice_template_3_en.html",
            TemplateType.TEMPLATE4: "invoice_template_4_en.html",
        },
        Language.GEORGIAN: {
            TemplateType.TEMPLATE1: "invoice_template_1_ka.html",
            TemplateType.TEMPLATE2: "invoice_template_2_ka.html",
            TemplateType.TEMPLATE3: "invoice_template_3_ka.html",
            TemplateType.TEMPLATE4: "invoice_template_4_ka.html",
        }
    }

    @classmethod
    def get_template(cls, language: str, template_type: str) -> Optional[Any]:
        """
        Get the appropriate template based on language and template type.

        :param: language: Language code (en or ka)
        :param: template_type: Template type identifier

        :return: Template object or None if not found

        :raises: LanguageNotSupportedError: If the language is not supported
        """
        try:
            lang = Language(language)
        except ValueError:
            raise LanguageNotSupportedError(f"Language '{language}' is not supported")

        try:
            template_choice = TemplateType(template_type)
        except ValueError:
            logger.warning(f"Invalid template type: {template_type}, using TEMPLATE1")
            template_choice = TemplateType.TEMPLATE1

        template_path = cls.TEMPLATE_MAPPING.get(lang, {}).get(template_choice)

        if not template_path:
            logger.error(f"Template not found for {lang}:{template_choice}")
            return None

        return get_template(template_path)


class InvoiceGenerator:
    """
    Invoice generator class to generate
    invoice based on the given invoice data.

    :param invoice_data: Invoice data
    :param user: User object associated with the invoice
    """

    def __init__(self, invoice_data: Dict[str, Any], user: User) -> None:
        self.invoice_data = invoice_data
        self.user = user
        self.invoice_service = InvoiceService()

    def generate_invoice(self) -> bytes:
        """
        Generate invoice method which calls the private
        method to create the invoice.

        :return: PDF file of the invoice

        :raises:
            InvoiceGenerationError: If PDF generation fails
            LanguageNotSupportedError: If the language is not supported
        """
        return self._create_invoice()

    def _prepare_context(self) -> Dict[str, Any]:
        """
        Prepare context for the invoice template.

        :return: Context for the invoice template
        """
        total_amount, vat_total = (
            self.invoice_service.calculate_totals(self.invoice_data)
        )

        current_date_numeral = datetime.datetime.now()
        current_month = current_date_numeral.month
        current_day = current_date_numeral.day
        current_year = current_date_numeral.year
        current_date_ge = (f"{current_day} {MONTHS_IN_GEORGIAN[current_month]},"
                           f" {current_year}წ.")
        current_date_en = (f"{current_day} {MONTHS_IN_ENGLISH[current_month]},"
                           f" {current_year}")

        self.invoice_data.update(
            {
                "invoice_number": InvoiceNumberGenerator.generate(),
                "total_amount": round(total_amount, 2),
                "vat_total": round(vat_total, 2),
                "total_without_vat": round(total_amount - vat_total, 2),
                "receiver_ka": self.user.receiver_name_ka,
                "receiver_en": self.user.receiver_name_en,
                "receiver_id": self.user.identification_code,
                "date_now": current_date_ge,
                "date_now_en": current_date_en,
                "payer_ka": self.invoice_data["payer"].name_ka,
                "payer_en": self.invoice_data["payer"].name_en,
                "payer_id": self.invoice_data["payer"].identification_code,
                "payer_phone": self.invoice_data["payer"].phone_number or "",
                "bank_name_ka": self.user.bank_name_ka,
                "bank_name_en": self.user.bank_name_en,
                "bank_acc_num": self.user.bank_account_number,
                "bank_code": self.user.bank_code,
                "receiver_phone": self.user.phone_number or ""
             }
        )
        return self.invoice_data

    def _create_invoice(self) -> Union[bytes, str]:
        """
        Create invoice method which generates the invoice
        based on the given invoice data and returns the PDF file.

        :return: PDF file of the invoice or error message

        :raises:
            InvoiceGenerationError: If PDF generation fails
            LanguageNotSupportedError: If the language is not supported
        """
        language = self.invoice_data.get("language", "en")
        template_choice = self.invoice_data.get("template", "template1")
        template = TemplateSelector.get_template(language, template_choice)

        if not template:
            raise InvoiceGenerationError(f"Template not found for {language}:{template_choice}")

        context = self._prepare_context()
        output_html = template.render(context)

        try:
            pdf = HTML(string=output_html).write_pdf()
            logger.info("PDF generation successful")
            return pdf
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise InvoiceGenerationError(f"Failed to generate PDF: {e}")
