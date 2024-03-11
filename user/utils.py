from django.core import mail
import random
from django.template.loader import render_to_string

def sendVerificationEmail(user, email):
    verification_code = str(random.randint(0, 999999))
    while len(verification_code) < 6:
        verification_code = "0" + verification_code
    verification_code = f"{verification_code}"
    html_message = render_to_string('email_form.html', {'verification_code': verification_code})
    plain_message = f"Mã xác thực của bạn: {verification_code}"
    mail.send_mail(
        subject="Verification code",
        from_email="Wave Chat <wavechat@gmail.com>",
        message=plain_message,
        recipient_list=[email],
        html_message=html_message
    )
    userProfile = user.profile
    userProfile.verification_code = verification_code
    userProfile.save()