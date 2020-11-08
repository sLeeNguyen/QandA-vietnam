from django.core.mail import EmailMessage


class Util:
    @staticmethod
    def send_email(subject, body, from_email=None, recipient_list=None):
        """
        Easy wrapper for sending a single message to a recipient list. All members
        of the recipient list will see the other recipients in the 'To' field.
        """
        print('sending email to ' + recipient_list[0])
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=recipient_list)
        email.send()
