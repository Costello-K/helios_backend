from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from common.enums import QuizProgressStatus
from common.models import TimeStampedModel
from company.models import Company

User = get_user_model()


class Quiz(TimeStampedModel):
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    frequency = models.IntegerField(_('frequency'), null=True)

    class Meta:
        verbose_name = _('quiz')
        verbose_name_plural = _('quizzes')

    def __str__(self):
        return self.title[:50]

    def get_updated_or_created_question(self, question_data):
        question_id = question_data.get('id', None)
        question = self.questions.filter(id=question_id).first()
        if question_id and question.question_text != question_data.get('question_text'):
            question.question_text = question_data['question_text']
            question.save()
        elif not question_id:
            question = Question.objects.create(quiz=self, question_text=question_data['question_text'])

        return question

    def remove_unused_questions(self, immutable_question_ids):
        self.questions.exclude(id__in=immutable_question_ids).delete()

    def get_count_correct_answers(self, user_responses):
        correct_count = 0

        for quiz_question, user_question in zip(self.questions.all(), user_responses.get('questions'), strict=False):
            total_answers = quiz_question.answers.count()
            if total_answers != len(user_question.get('answers')) \
                    or quiz_question.question_text != user_question.get('question_text'):
                raise ValidationError(_('Question mismatch'))

            correct_answer = 0
            for quiz_answer, user_answer \
                    in zip(quiz_question.answers.all(), user_question.get('answers'), strict=False):
                if quiz_answer.text != user_answer.get('text'):
                    raise ValidationError(_('Answer mismatch'))

                if quiz_answer.is_right == user_answer.get('is_right'):
                    correct_answer += 1
                else:
                    correct_answer -= 1

            if correct_answer > 0:
                correct_count += correct_answer/total_answers

        return correct_count


class Question(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, verbose_name=_('quiz'), on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(_('question text'), max_length=255)

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')

    def __str__(self):
        return f'id_{self.id}: {self.question_text[:30]}'

    def update_answers(self, answers_data):
        immutable_answers_ids = []
        for answer_data in answers_data:
            answer = self.answers.filter(**answer_data)
            if answer.exists():
                immutable_answers_ids.append(answer.first().id)

        remove_answer = self.answers.exclude(id__in=immutable_answers_ids)
        self.answers.remove(*remove_answer)

        for answer in answers_data:
            new_answer, create = Answer.objects.get_or_create(**answer)
            self.answers.add(new_answer)

        self.save()


class Answer(models.Model):
    question = models.ManyToManyField(Question, verbose_name=_('question'), related_name='answers')
    text = models.CharField(_('text'), max_length=255)
    is_right = models.BooleanField(_('is right'), default=False)

    class Meta:
        verbose_name = _('answer')
        verbose_name_plural = _('answers')

    def __str__(self):
        return f'id_{self.id}: {self.text[:30]}'


class UserQuizResult(TimeStampedModel):
    participant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('participant'),
                                    related_name='quiz_participant_result')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, verbose_name=_('company'),
                                related_name='quiz_company_result')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, verbose_name=_('quiz'),
                             related_name='quiz_result')

    correct_answers = models.FloatField(_('correct answers'), default=0)
    total_questions = models.PositiveIntegerField(_('total questions'), default=0)
    progress_status = models.CharField(_('progress status'),
                                       choices=[(status.name, status.value) for status in QuizProgressStatus],
                                       default=QuizProgressStatus.STARTED.value)

    correct_answers_collector = models.FloatField(_('correct answers collector'), default=0)
    total_questions_collector = models.PositiveIntegerField(_('total questions collector'), default=0)
    correct_company_answers_collector = models.FloatField(_('correct company answers collector'), default=0)
    total_company_questions_collector = models.PositiveIntegerField(_('total company questions collector'), default=0)

    quiz_time = models.DurationField(_('quiz time'), default=timezone.timedelta())
    company_average_score = models.DecimalField(_('company average score'), default=0, max_digits=5, decimal_places=2)
    user_rating = models.DecimalField(_('user rating'), default=0, max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = _('user quiz result')
        verbose_name_plural = _('user quiz results')

    def quiz_completed(self, user_responses):
        if self.progress_status != QuizProgressStatus.STARTED.value:
            raise ValidationError(_('The quiz has already been completed'))

        last_completed_result = self.get_last_user_quiz_result(
            participant=self.participant, progress_status=QuizProgressStatus.COMPLETED.value)
        last_company_completed_result = self.get_last_user_quiz_result(
            participant=self.participant, company=self.company, progress_status=QuizProgressStatus.COMPLETED.value)

        self.total_questions = self.quiz.questions.count()
        self.correct_answers = self.quiz.get_count_correct_answers(user_responses)
        self.quiz_time = timezone.now() - self.created_at

        self.update_property_without_save('correct_answers_collector', last_completed_result, self.correct_answers)
        self.update_property_without_save('total_questions_collector', last_completed_result, self.total_questions)
        self.update_property_without_save('correct_company_answers_collector', last_company_completed_result,
                                          self.correct_answers)
        self.update_property_without_save('total_company_questions_collector', last_company_completed_result,
                                          self.total_questions)

        self.user_rating = self.get_user_rating()
        self.company_average_score = self.get_company_average_score()

        self.progress_status = QuizProgressStatus.COMPLETED.value
        self.save()

    @staticmethod
    def get_last_user_quiz_result(**kwargs):
        return UserQuizResult.objects.filter(**kwargs).order_by('-updated_at').first()

    def get_user_rating(self):
        new_rating = self.user_rating

        if self.total_questions_collector > 0:
            new_rating = Decimal(
                (self.correct_answers_collector / self.total_questions_collector) * 100).quantize(Decimal('1.00'))

        return new_rating

    def get_company_average_score(self):
        new_company_average_score = self.company_average_score

        if self.total_company_questions_collector > 0:
            new_company_average_score = Decimal(
                (self.correct_company_answers_collector / self.total_company_questions_collector) * 100) \
                .quantize(Decimal('1.00'))

        return new_company_average_score

    def update_property_without_save(self, attribute_name, instance, value):
        new_value = value

        if instance:
            new_value += getattr(instance, attribute_name)

        setattr(self, attribute_name, new_value)
