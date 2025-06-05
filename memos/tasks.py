from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import VoiceMemo
from datetime import datetime, timedelta
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)
from django.conf import settings



def send_daily_summary():
    today = datetime.now().date()
    memos = VoiceMemo.objects.filter(created_at__date=today)

    email_body = render_to_string('email_summary.html', {'memos': memos})

    send_mail(
        subject='Your Daily Voice Memo Summary',
        message='',
        html_message=email_body,
        from_email='noreply@voiceassistant.local',
        recipient_list=['you@example.com'],
    )
