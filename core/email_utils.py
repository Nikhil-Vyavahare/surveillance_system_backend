from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_email_with_image(recipient_email, image_path, description):
    print("FROM:", settings.EMAIL_HOST_USER)
    subject = 'Detection Alert: Garbage or Open Drainage'
    from_email = settings.DEFAULT_FROM_EMAIL
    text_content = f'Detection: {description}'
    html_content = f'<p>Detection: {description}</p>'

    msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
    msg.attach_alternative(html_content, "text/html")
    with open(image_path, 'rb') as img:
        msg.attach('detection.jpg', img.read(), 'image/jpeg')
    msg.send()