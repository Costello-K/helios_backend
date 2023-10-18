from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from company.models import Company
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

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'avatar']

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
        email = validated_data.get('email')
        avatar = validated_data.get('avatar')

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
        # check that the email field is not empty
        if not email:
            raise serializers.ValidationError(
                {'email': _('Email field is required.')}
            )
        # check that the email field is not use
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': _('Email is already in use.')}
            )
        # check the avatar file size to the maximum allowed size
        if avatar and avatar.size > (settings.USER_AVATAR_MAX_SIZE_MB * 1024 * 1024):
            raise serializers.ValidationError(
                {'avatar': _('Maximum image size allowed is {} Mb').format(settings.USER_AVATAR_MAX_SIZE_MB)}
            )

        # create a new user
        # is_active=False to require user activation via email
        user = User.objects.create_user(**validated_data, password=password, is_active=False)

        return user

    def to_representation(self, instance):
        # Initialize the data dictionary with the default representation
        data = super().to_representation(instance)

        request = self.context.get('request')
        request_method = request.method if request else None
        # Get 'avatar' value from initial_data or set it to None
        avatar = self.initial_data.get('avatar') if hasattr(self, 'initial_data') else None

        if request_method in ['PUT', 'PATCH']:
            # If 'avatar' in the request is an empty string, set it to the default avatar URL
            if avatar == '':
                data['avatar'] = settings.DEFAULT_USER_AVATAR_URL
            # If 'avatar' in the request is not empty, set it to the user's avatar URL
            elif avatar:
                data['avatar'] = instance.avatar.url

        return data


class UserDetailSerializer(UserSerializer):
    """
        Serializer class for detailed User objects.
        This serializer extends the UserSerializer to include additional details, such as the user's avatar.

        Attributes:
            avatar (SerializerMethodField): A method field that serializes the user's avatar URL.
        This serializer is used for displaying detailed information about a user, including their avatar if available.
        """
    avatar = serializers.SerializerMethodField()

    @staticmethod
    def get_avatar(user):
        """
        Get the user's avatar URL.
        This method retrieves the URL of the user's avatar if it's available or provides a default avatar URL if not.
        """
        if hasattr(user, 'avatar') and user.avatar and hasattr(user.avatar, 'file'):
            return user.avatar.url
        # if the image does not exist, we send the image for the user by default
        return settings.DEFAULT_USER_AVATAR_URL


class RequestToCompanySerializer(serializers.ModelSerializer):
    from company.serializers import CompanySerializer

    company = CompanySerializer(read_only=True)
    sender = UserDetailSerializer(read_only=True)

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
            instance.reject()

        return instance
