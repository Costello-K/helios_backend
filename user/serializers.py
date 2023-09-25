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
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'confirm_password']
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

        # check that the 'password' field is not empty
        if password is None:
            raise serializers.ValidationError('Password is required for user creation.')
        # check that the 'password' matches the 'confirm_password' field
        if password != confirm_password:
            raise serializers.ValidationError('Password and confirm_password are different.')

        # create a new user
        user = User.objects.create_user(**validated_data, password=password)

        return user
