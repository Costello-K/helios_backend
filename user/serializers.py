from django.conf import settings
from rest_framework import serializers
from django.contrib.auth import get_user_model

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
        ordering = ['created_at']

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
                {'password': 'Password is required for user creation.'}
            )
        # check that the 'password' matches the 'confirm_password' field
        if password != confirm_password:
            raise serializers.ValidationError(
                {'confirm_password': 'Password and confirm_password are different.'}
            )
        # check that the email field is not empty
        if not email:
            raise serializers.ValidationError(
                {'email': 'Email field is required.'}
            )
        # check that the email field is not use
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Email is already in use.'}
            )
        # check the avatar file size to the maximum allowed size
        if avatar and avatar.size > (settings.USER_AVATAR_MAX_SIZE_MB * 1024 * 1024):
            raise serializers.ValidationError(
                {'avatar': f'Maximum image size allowed is {settings.USER_AVATAR_MAX_SIZE_MB}Mb'}
            )

        # create a new user
        # is_active=False to require user activation via email
        user = User.objects.create_user(**validated_data, password=password, is_active=False)

        return user


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
        if user.avatar and user.avatar.file:
            return user.avatar.url
        # if the image does not exist, we send the image for the user by default
        return settings.DEFAULT_USER_AVATAR_URL
