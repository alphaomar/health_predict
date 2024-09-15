# pharmacy/utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_notification_email(subject, template, context, recipient_list):
    message = render_to_string(template, context)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
    )