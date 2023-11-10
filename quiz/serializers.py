from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError

from common.enums import QuizProgressStatus
from company.models import Company
from company.serializers import CompanySerializer
from internship_meduzzen_backend.settings import EXCEL_FILE_MAX_SIZE_MB, MIN_COUNT_ANSWERS, MIN_COUNT_QUESTIONS
from services.parsers.converter import convert_file_to_data
from user.serializers import UserSerializer

from .models import Answer, Question, Quiz, UserQuizResult

User = get_user_model()


class AnswerSerializer(serializers.ModelSerializer):
    is_right = serializers.BooleanField()

    class Meta:
        model = Answer
        exclude = ('question', )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not self.context.get('full_access'):
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
    last_quiz_completion_time = serializers.SerializerMethodField(read_only=True)
    auth_user_last_completed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

    @staticmethod
    def get_last_quiz_completion_time(quiz):
        last_user_quiz_result = quiz.quiz_result.filter(
            progress_status=QuizProgressStatus.COMPLETED.value
        )

        if not last_user_quiz_result.exists():
            return None

        return last_user_quiz_result.order_by('updated_at').last().updated_at

    def get_auth_user_last_completed(self, quiz):
        auth_user = self.context['request'].user
        if not auth_user:
            return None

        user_quiz_results = quiz.quiz_result.filter(participant=auth_user)
        if not user_quiz_results.exists():
            return None

        last_user_quiz_result = user_quiz_results.order_by('updated_at').last()
        return {
            'completed': last_user_quiz_result.progress_status == QuizProgressStatus.COMPLETED.value,
            'created_at': last_user_quiz_result.created_at,
            'updated_at': last_user_quiz_result.updated_at,
        }

    def to_representation(self, instance):
        if isinstance(instance, list):
            return {'quizzes': [self.to_representation(quiz) for quiz in instance]}

        data = super().to_representation(instance)

        if not self.context.get('full_access'):
            data['last_quiz_completion_time'] = None

        return data


class QuizDetailSerializer(QuizSerializer):
    questions = QuestionSerializer(many=True)

    class Meta(QuizSerializer.Meta):
        pass

    def to_internal_value(self, data, is_file=True):
        if self.context['request'].query_params.get('export_file') and is_file:
            file = data.get('file', None)
            if not file:
                raise serializers.ValidationError({'message': _('File not found')})
            if file.size > (EXCEL_FILE_MAX_SIZE_MB * 1024 * 1024):
                raise serializers.ValidationError(
                    {'file': _('Maximum file size allowed is {} Mb').format(EXCEL_FILE_MAX_SIZE_MB)}
                )

            quiz_list_data = convert_file_to_data(file)
            if self.context['view'].action == 'create':
                validated_quiz_list_data = OrderedDict()
                for index, validated_quiz_data \
                        in enumerate(self.to_internal_value(data, is_file=False) for data in quiz_list_data):
                    fields.set_value(validated_quiz_list_data, f'{index}', validated_quiz_data)
                return validated_quiz_list_data
            if self.context['view'].action == 'partial_update':
                return super().to_internal_value(quiz_list_data[0])

            raise serializers.ValidationError({'message': _('Action not supported')})

        return super().to_internal_value(data)

    def create(self, validated_data):
        is_export_file = self.context['request'].query_params.get('export_file')
        is_create = self.context['view'].action == 'create'
        company_pk = self.context['request'].parser_context['kwargs']['company_pk']
        company = get_object_or_404(Company, pk=company_pk)

        with transaction.atomic():
            quizzes = []
            if is_export_file and is_create:
                for quiz_key in validated_data:
                    quizzes.append(self.create_quiz(company, validated_data[quiz_key]))
            else:
                quizzes.append(self.create_quiz(company, validated_data))

        return quizzes

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
                    immutable_question_ids.append(question.first().id)
            instance.remove_unused_questions(immutable_question_ids)

            self.create_or_update_questions(instance, questions_data)
            instance.save()

            return instance

    def create_quiz(self, company, validated_data):
        validated_data['company'] = company
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        self.create_or_update_questions(quiz, questions_data)
        return quiz

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
    class Meta:
        model = UserQuizResult
        fields = '__all__'


class UserQuizResultDetailSerializer(UserQuizResultSerializer):
    participant = UserSerializer(read_only=True)
    company = CompanySerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta(UserQuizResultSerializer.Meta):
        pass


class QuizAnalyticsSerializer(serializers.ModelSerializer):
    quiz_results = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'quiz_results')

    @staticmethod
    def get_quiz_results(quiz):
        queryset = UserQuizResult.objects.filter(
            quiz=quiz,
            progress_status=QuizProgressStatus.COMPLETED.value,
        ).order_by('updated_at')

        serialized_results = UserQuizResultSerializer(queryset, many=True)
        return serialized_results.data


class UserAnalyticsSerializer(serializers.ModelSerializer):
    quiz_results = serializers.SerializerMethodField(read_only=True)
    companies = serializers.SerializerMethodField(read_only=True)
    quizzes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'quiz_results', 'companies', 'quizzes')

    @staticmethod
    def get_quiz_results(user):
        queryset = UserQuizResult.objects.filter(
            participant=user,
            progress_status=QuizProgressStatus.COMPLETED.value,
        ).order_by('updated_at')

        serialized_results = UserQuizResultSerializer(queryset, many=True)
        return serialized_results.data

    def get_companies(self, user):
        queryset = Company.objects.filter(companymember__member=user)

        serialized_results = CompanySerializer(queryset, many=True, context=self.context)
        return serialized_results.data

    def get_quizzes(self, user):
        queryset = Quiz.objects.filter(quiz_result__participant=user).distinct()

        serialized_results = QuizSerializer(queryset, many=True, context=self.context)
        return serialized_results.data


class CompanyAnalyticsSerializer(serializers.ModelSerializer):
    quiz_results = serializers.SerializerMethodField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)
    quizzes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'quiz_results', 'members', 'quizzes')

    def get_quiz_results(self, company):
        user_id = self.context['request'].query_params.get('user_id', None)

        queryset = UserQuizResult.objects.filter(
            company=company,
            progress_status=QuizProgressStatus.COMPLETED.value,
        ).order_by('updated_at')

        if user_id:
            queryset = queryset.filter(participant_id=user_id)

        serialized_results = UserQuizResultSerializer(queryset, many=True)
        return serialized_results.data

    def get_members(self, company):
        user_id = self.context['request'].query_params.get('user_id', None)
        if user_id:
            return None

        queryset = User.objects.filter(companymember__company=company)

        serialized_results = UserSerializer(queryset, many=True, context=self.context)
        return serialized_results.data

    def get_quizzes(self, company):
        queryset = Quiz.objects.filter(company=company)

        serialized_results = QuizSerializer(queryset, many=True, context=self.context)
        return serialized_results.data
