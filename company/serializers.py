from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.enums import InvitationStatus, QuizProgressStatus, RequestStatus
from user.serializers import UserSerializer

from .models import Company, CompanyMember, InvitationToCompany

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)
    is_member = serializers.SerializerMethodField(read_only=True)
    is_active_request = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'visibility', 'owner', 'is_admin', 'is_member', 'is_active_request')

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        company = Company.objects.create(**validated_data)
        return company

    def get_is_admin(self, company):
        if self.context and self.context.get('request'):
            user = self.context['request'].user
            if user and user.is_authenticated:
                return company.companymember_set.filter(member=self.context.get('request').user, admin=True).exists()
        return None

    def get_is_member(self, company):
        if self.context and self.context.get('request'):
            user = self.context['request'].user
            if user and user.is_authenticated:
                return company.companymember_set.filter(member=self.context.get('request').user).exists()
        return None

    def get_is_active_request(self, company):
        if self.context and self.context.get('request'):
            user = self.context['request'].user
            if user and user.is_authenticated:
                return company.requesttocompany_set.filter(
                    sender=self.context.get('request').user,
                    status=RequestStatus.PENDING.value
                ).exists()
        return None


class CompanyMemberSerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True)
    last_quiz_completion_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CompanyMember
        exclude = ('company', )

    @staticmethod
    def get_last_quiz_completion_time(company_member):
        last_user_quiz_result = company_member.member.quiz_participant_result.filter(
            company=company_member.company,
            progress_status=QuizProgressStatus.COMPLETED.value
        )

        if not last_user_quiz_result.exists():
            return None

        return last_user_quiz_result.order_by('updated_at').last().updated_at


class InvitationToCompanySerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    recipient = UserSerializer(read_only=True)

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
            instance.status_update(InvitationStatus.DECLINED.value)

        return instance
