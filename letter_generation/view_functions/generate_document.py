from email.message import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
import tempfile
import os
import smtplib
from django.conf import settings
from decimal import Decimal
from bson import Decimal128
from xhtml2pdf import pisa
from io import BytesIO

from employee_management.models import Employee
import logging

logger = logging.getLogger(__name__)

def generate_pdf(document_request):
    # Build the template name from the document type
    template_name = f"documents/{document_request.document_type.lower().replace(' ', '_')}.html"

    # Get employee data using the document request's user email
    employee = get_object_or_404(Employee, email=document_request.user.username)

    # Convert allowance and salary to Decimal from Decimal128
    allowance_decimal = Decimal(employee.allowance.to_decimal())
    salary_decimal = Decimal(employee.basic_salary.to_decimal())

    # Context for the template rendering
    context = {
        "employee_name": document_request.user.get_full_name(),
        "job_title": employee.role,
        "employee_id": employee.id,
        "department": employee.department,
        "start_date": employee.joining_date,
        "end_date": now().strftime("%Y-%m-%d"),
        "basic_salary": employee.basic_salary,
        "allowances": employee.allowance,
        "gross_salary": allowance_decimal + salary_decimal,
        "company_name": settings.COMPANY_NAME,
        "date": now().strftime("%Y-%m-%d"),
        "document_title": document_request.document_type,
        "content": document_request.reason,
    }

    # Render HTML string using the provided template and context
    html_string = render_to_string(template_name, context)

    # Create a temporary PDF file
    pdf_file = BytesIO()

    # Convert HTML to PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)

    # Check for errors
    if pisa_status.err:
        logger.error(f"Failed to generate PDF: {pisa_status.err}")
        return None

    # Save the generated PDF to a file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_file.getvalue())
        temp_pdf_path = temp_pdf.name

    # Return the file path to the generated PDF
    return temp_pdf_path

def send_document_email(document_request):
    try:
        # Email settings from Django's settings
        EMAIL_HOST = settings.EMAIL_HOST
        EMAIL_PORT = settings.EMAIL_PORT
        EMAIL_HOST_USER = settings.EMAIL_HOST_USER
        EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD

        # Generate the PDF for the document request
        pdf_path = generate_pdf(document_request)

        # If PDF generation fails, log and return
        if not pdf_path:
            logger.error("PDF generation failed. Email not sent.")
            return

        # Compose the email body and subject
        body = (
            f"Dear {document_request.user.get_full_name()},\n\n"
            f"Your {document_request.document_type} has been approved. "
            f"Please find the attached document.\n\nBest Regards,\nHR Team"
        )
        subject = f"{document_request.document_type} - Approved"

        # Create the email message
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_HOST_USER
        msg["To"] = document_request.user.email
        msg.set_content(body)

        # Attach the generated PDF to the email
        with open(pdf_path, "rb") as file:
            file_data = file.read()
            file_name = os.path.basename(pdf_path)
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

        # Send the email using SMTP
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        # Update the document request status and log success
        document_request.sent_status = True
        document_request.save()

        logger.info(f"Email sent successfully to {document_request.user.email} with attached PDF.")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
