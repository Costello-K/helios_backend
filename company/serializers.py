from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.serializers import UserDetailSerializer

from .models import Company, CompanyMember, InvitationToCompany

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        company = Company.objects.create(**validated_data)
        return company


class CompanyMemberSerializer(serializers.ModelSerializer):
    member = UserDetailSerializer(read_only=True)

    class Meta:
        model = CompanyMember
        exclude = ('company', )


class InvitationToCompanySerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    recipient = UserDetailSerializer(read_only=True)

    class Meta:
        model = InvitationToCompany
        fields = '__all__'

    def create(self, validated_data):
        company_pk = self.context['request'].parser_context['kwargs']['company_pk']
        recipient_pk = self.context['request'].parser_context['kwargs']['pk']

        company = get_object_or_404(Company, pk=company_pk)
        recipient = get_object_or_404(User, pk=recipient_pk)

        if company.is_owner(recipient):
            raise serializers.ValidationError(
                {'message': _('The owner cannot be a member of the company.')}
            )

        validated_data['company'] = company
        validated_data['recipient'] = recipient

        invitation = InvitationToCompany.objects.create(**validated_data)
        return invitation

    def update(self, instance, validated_data):
        # user accepted or declined the join request with data = { 'confirm': true | false }
        confirm = self.context['request'].data['confirm']

        if confirm:
            instance.accept()
        else:
            instance.decline()

        return instance
