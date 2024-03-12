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
    
def sendForgetPasswordEmail(reset_password_token):
    user = reset_password_token.user
    forget_password_token = "{}".format(reset_password_token.key)
    
    greetings = "Hi {}!".format(reset_password_token.user.username)
    email_html_content = "<html><body><p>{greetings}</p> \
                        <p>Please use this Token for password Reset on SChat website: <b>{token}</b></p></body></html>".format(
                            greetings=greetings,
                            token=forget_password_token
                        )

    mail.send_mail(
        subject="Forget Password Token",
        from_email='Wave Chat <wavechat@gmail.com>',
        message=greetings,
        recipient_list=[user.email],
        html_message=email_html_content
    )