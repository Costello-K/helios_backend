from rest_framework import serializers

from user.serializers import UserDetailSerializer

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        company = Company.objects.create(**validated_data)
        return company
