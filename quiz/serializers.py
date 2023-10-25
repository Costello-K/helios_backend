from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from company.models import Company
from company.serializers import CompanySerializer
from internship_meduzzen_backend.settings import MIN_COUNT_ANSWERS, MIN_COUNT_QUESTIONS
from user.serializers import UserSerializer

from .models import Answer, Question, Quiz, UserQuizResult


class AnswerSerializer(serializers.ModelSerializer):
    is_right = serializers.BooleanField()

    class Meta:
        model = Answer
        exclude = ('question', )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not self.context.get('add_right_answer'):
            data['is_right'] = None

        return data


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Question
        exclude = ('quiz', )


class QuizSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizDetailSerializer(QuizSerializer):
    questions = QuestionSerializer(many=True)

    class Meta(QuizSerializer.Meta):
        pass

    def create(self, validated_data):
        company_pk = self.context['request'].parser_context['kwargs']['company_pk']
        company = get_object_or_404(Company, pk=company_pk)
        validated_data['company'] = company
        questions_data = validated_data.pop('questions')

        with transaction.atomic():
            quiz = Quiz.objects.create(**validated_data)
            self.create_or_update_questions(quiz, questions_data)

        return quiz

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.frequency = validated_data.get('frequency', instance.frequency)
            questions_data = validated_data.pop('questions')

            immutable_question_ids = []
            for question_data in questions_data:
                question = instance.questions.filter(id=question_data.get('id'), quiz=instance)
                if question.exists():
                    immutable_question_ids.append(question.first())
            instance.remove_unused_questions(immutable_question_ids)

            self.create_or_update_questions(instance, questions_data)
            instance.save()

            return instance

    @staticmethod
    def create_or_update_questions(quiz, questions_data):
        # add or change questions
        for question_data in questions_data:
            question = quiz.get_updated_or_created_question(question_data)

            # add or change answers
            answers_data = question_data.pop('answers')
            question.update_answers(answers_data)

    @staticmethod
    def validate_questions(questions_data):
        if len(questions_data) < MIN_COUNT_QUESTIONS:
            raise ValidationError(_('A quiz must have at least {} questions.').format(MIN_COUNT_QUESTIONS))

        for question_data in questions_data:
            answers_data = question_data.get('answers')

            if len(answers_data) < MIN_COUNT_ANSWERS:
                raise serializers.ValidationError(
                    _('A question must have at least {} answers.').format(MIN_COUNT_ANSWERS)
                )
            if not any(answer.get('is_right') for answer in answers_data):
                raise serializers.ValidationError(_('At least one answer must be marked as correct.'))

        return questions_data


class UserQuizResultSerializer(serializers.ModelSerializer):
    participant = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = UserQuizResult
        fields = '__all__'
