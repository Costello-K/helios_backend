import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory import Faker, LazyAttribute, PostGenerationMethodCall, Sequence, SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyInteger

from common.enums import QuizProgressStatus
from company.models import Company, CompanyMember, InvitationToCompany
from quiz.models import Answer, Question, Quiz, UserQuizResult
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
    description = Faker('text')
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


class QuizFactory(DjangoModelFactory):
    class Meta:
        model = Quiz

    company = SubFactory(CompanyFactory)
    title = Sequence(lambda n: f'Quiz_{n}')
    description = Faker('text')
    frequency = FuzzyInteger(1, 10)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    quiz = SubFactory(QuizFactory)
    question_text = Sequence(lambda n: f'Question_{n}')


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = Answer

    question = SubFactory(QuestionFactory)
    text = Sequence(lambda n: f'Answer_{n}')
    is_right = FuzzyChoice([True, False])

    @factory.post_generation
    def question(self, create, extracted, **kwargs):
        if not create or not extracted:
            # Simple build, or nothing to add, do nothing.
            return

        # Add the iterable of groups using bulk addition
        self.question.add(*extracted)


class TrueAnswerFactory(AnswerFactory):
    class Meta:
        model = Answer

    is_right = True


class FalseAnswerFactory(AnswerFactory):
    class Meta:
        model = Answer

    is_right = False


class UserQuizResultFactory(DjangoModelFactory):
    class Meta:
        model = UserQuizResult

    participant = SubFactory(UserFactory)
    company = SubFactory(CompanyFactory)
    quiz = SubFactory(QuizFactory)


class UserQuizResultCompletionFactory(UserQuizResultFactory):
    class Meta:
        model = UserQuizResult

    correct_answers = Faker('random_int', min=0, max=5)
    total_questions = Faker('random_int', min=5, max=10)
    progress_status = QuizProgressStatus.COMPLETED.value
    correct_answers_collector = Faker('random_int', min=0, max=20)
    total_questions_collector = Faker('random_int', min=20, max=40)
    correct_company_answers_collector = Faker('random_int', min=0, max=20)
    total_company_questions_collector = Faker('random_int', min=20, max=40)
    quiz_time = Sequence(lambda n: timezone.timedelta(minutes=n))
    company_average_score = Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    user_rating = Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
