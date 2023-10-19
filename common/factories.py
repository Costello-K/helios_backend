import factory
from django.contrib.auth import get_user_model
from factory import LazyAttribute, PostGenerationMethodCall, Sequence, SubFactory
from factory.django import DjangoModelFactory

from company.models import Company, CompanyMember, InvitationToCompany
from user.models import RequestToCompany

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'user_{n}')
    first_name = Sequence(lambda n: f'First name {n}')
    last_name = Sequence(lambda n: f'Last name {n}')
    email = LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = PostGenerationMethodCall('set_password', 'password')


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    name = Sequence(lambda n: f'Company_{n}')
    description = factory.Faker('text')
    visibility = True
    owner = SubFactory(UserFactory)


class CompanyMemberFactory(DjangoModelFactory):
    class Meta:
        model = CompanyMember

    member = SubFactory(UserFactory)
    company = SubFactory(CompanyFactory)


class CompanyMemberAdminFactory(CompanyMemberFactory):
    class Meta:
        model = CompanyMember

    admin = True


class InvitationToCompanyFactory(DjangoModelFactory):
    class Meta:
        model = InvitationToCompany

    recipient = SubFactory(UserFactory)
    company = SubFactory(CompanyFactory)


class RequestToCompanyFactory(DjangoModelFactory):
    class Meta:
        model = RequestToCompany

    sender = SubFactory(UserFactory)
    company = SubFactory(CompanyFactory)
