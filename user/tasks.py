from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from internship_meduzzen_backend.celery import app
from internship_meduzzen_backend.settings import EMAIL_HOST_USER
from services.get_list_quizzes import get_available_user_quiz_list

User = get_user_model()


@app.task
def send_email_access_to_quiz_is_open():
    """
    The task is to send an email notification about the expiration of the restriction on re-taking the quiz.
    """
    users = User.objects.all()
    for user in users:
        if user.email:
            available_quizzes = get_available_user_quiz_list(user.id)

            if available_quizzes:
                subject = _('Available quizzes today')

                message_data = [_('{index}: Company "{name}". Quiz "{title}".').format(
                    index=index,
                    name=quiz.company.name,
                    title=quiz.title
                ) for index, quiz in enumerate(available_quizzes, start=1)]

                message = _('Available quizzes for user {username} ({first_name} {last_name}):\n').format(
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )

                message += '\n'.join(message_data)

                send_mail(subject, message, EMAIL_HOST_USER, [user.email])
