from django.conf import settings as django_settings
from djoser import email


class ActivationEmail(email.ActivationEmail):
    """
    Class for sending an account activation email based on the DJOSER class
    """
    # Override activation email template
    template_name = 'account_email_activation.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['frontend_site_name'] = django_settings.ALLOWED_HOSTS[0]

        return context


class PasswordResetEmail(email.PasswordResetEmail):
    """
    Class for sending a password reset email based on the DJOSER class
    """
    # Override password reset email template
    template_name = 'account_password_reset.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['frontend_site_name'] = django_settings.ALLOWED_HOSTS[0]

        return context


class UsernameResetEmail(email.UsernameResetEmail):
    """
    Class for sending a username reset email based on the DJOSER class
    """
    # Override username reset email template
    template_name = 'account_username_reset.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['frontend_site_name'] = django_settings.ALLOWED_HOSTS[0]

        return context
