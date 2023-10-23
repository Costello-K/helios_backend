from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel
from company.models import Company


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
