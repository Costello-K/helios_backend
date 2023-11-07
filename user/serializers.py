from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.enums import QuizProgressStatus, RequestStatus
from company.models import Company
from internship_meduzzen_backend.settings import DEFAULT_USER_AVATAR_URL, USER_AVATAR_MAX_SIZE_MB
from user.models import RequestToCompany

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for User objects.

    Attributes:
        password (CharField): A write-only field for user password.
        confirm_password (CharField): A write-only field to confirm the user password.
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    rating = serializers.SerializerMethodField(read_only=True)
    is_company_admin = serializers.SerializerMethodField(read_only=True)
    is_company_member = serializers.SerializerMethodField(read_only=True)
    is_active_invitation = serializers.SerializerMethodField(read_only=True)
    last_company_quiz_for_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'avatar', 'rating',
            'is_company_admin', 'is_company_member', 'is_active_invitation', 'last_company_quiz_for_user',
        ]

    @staticmethod
    def get_rating(user):
        last_user_quiz_result = user.quiz_participant_result.filter(
            progress_status=QuizProgressStatus.COMPLETED.value)

        if not last_user_quiz_result.exists():
            return None

        return last_user_quiz_result.last().user_rating

    def get_is_company_admin(self, user):
        if self.context and self.context.get('request'):
            company_id = self.context['request'].query_params.get('company_id')
            if company_id:
                return user.my_admin_companies.filter(id=company_id).exists()
        return None

    def get_is_company_member(self, user):
        if self.context and self.context.get('request'):
            company_id = self.context['request'].query_params.get('company_id')
            if company_id:
                return user.my_member_companies.filter(id=company_id).exists()
        return None

    def get_is_active_invitation(self, user):
        if self.context and self.context.get('request'):
            company_id = self.context['request'].query_params.get('company_id')
            if company_id:
                return user.my_invitations.filter(company_id=company_id, status=RequestStatus.PENDING.value).exists()
        return None

    def get_last_company_quiz_for_user(self, user):
        company_id = self.context['request'].query_params.get('company_id')
        if not company_id:
            return None

        user_company_quiz_results = user.quiz_participant_result.filter(company_id=company_id)
        if not user_company_quiz_results.exists():
            return None

        last_user_company_quiz_result = user_company_quiz_results.order_by('updated_at').last()
        return {
            'completed': last_user_company_quiz_result.progress_status == QuizProgressStatus.COMPLETED.value,
            'quiz_title': last_user_company_quiz_result.quiz.title,
            'created_at': last_user_company_quiz_result.created_at,
            'updated_at': last_user_company_quiz_result.updated_at,
        }

    def create(self, validated_data):
        """
        Create a new User object.

        Args:
            validated_data (dict): The validated data from the serialized request.
        Returns:
            User: The newly created User object.
        Raises:
            serializers.ValidationError: If the password is missing or does not match the confirm_password field.
        """
        # extract the fields from validated_data or set it to None if absent
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        # check that the 'password' field is not empty
        if password is None:
            raise serializers.ValidationError(
                {'password': _('Password is required for user creation.')}
            )
        # check that the 'password' matches the 'confirm_password' field
        if password != confirm_password:
            raise serializers.ValidationError(
                {'confirm_password': _('Password and confirm_password are different.')}
            )

        # create a new user
        # is_active=False to require user activation via email
        user = User.objects.create_user(**validated_data, password=password, is_active=False)

        return user

    def update(self, instance, validated_data):
        if self.context['request'].data.get('avatar') == '':
            validated_data['avatar'] = None

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        # Initialize the data dictionary with the default representation
        data = super().to_representation(instance)

        if hasattr(instance, 'avatar') and instance.avatar and hasattr(instance.avatar, 'file'):
            data['avatar'] = instance.avatar.url
        else:
            # if the image does not exist, we send the image for the user by default
            data['avatar'] = DEFAULT_USER_AVATAR_URL

        return data

    @staticmethod
    def validate_avatar(value):
        if value and value.size > (USER_AVATAR_MAX_SIZE_MB * 1024 * 1024):
            raise serializers.ValidationError(
                _('Maximum image size allowed is {} Mb').format(USER_AVATAR_MAX_SIZE_MB)
            )
        return value

    @staticmethod
    def validate_email(value):
        if not value:
            raise serializers.ValidationError(_('Email field is required.'))
        # check that the email field is not use
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Email is already in use.'))

        return value


class RequestToCompanySerializer(serializers.ModelSerializer):
    from company.serializers import CompanySerializer

    company = CompanySerializer(read_only=True)
    sender = UserSerializer(read_only=True)

    class Meta:
        model = RequestToCompany
        fields = '__all__'

    def create(self, validated_data):
        company_pk = self.context['request'].parser_context['kwargs']['pk']

        validated_data['company'] = get_object_or_404(Company, pk=company_pk)
        validated_data['sender'] = self.context['request'].user

        invitation = RequestToCompany.objects.create(**validated_data)
        return invitation

    def update(self, instance, validated_data):
        # company owner approved or rejected the join request with data = { 'confirm': true | false }
        confirm = self.context['request'].data['confirm']

        if confirm:
            instance.approve()
        else:
            instance.status_update(RequestStatus.REJECTED.value)

        return instance
