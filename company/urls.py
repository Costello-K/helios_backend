from django.urls import path

from .views import CompanyViewSet, InvitationToCompanyViewSet, RequestToCompanyViewSet

urlpatterns = [
    path('', CompanyViewSet.as_view({'get': 'list', 'post': 'create'}), name='company-list'),
    path(
        '<int:pk>/',
        CompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='company-detail',
    ),
    path('<int:pk>/members/', CompanyViewSet.as_view({'get': 'members'}), name='company-members'),
    path('<int:pk>/remove_me/', CompanyViewSet.as_view({'delete': 'remove_me'}), name='company-remove-me'),
    path(
        '<int:company_pk>/remove_user/<int:pk>/',
        CompanyViewSet.as_view({'delete': 'remove_user'}),
        name='company-remove-user',
    ),

    path(
        '<int:company_pk>/invitations/',
        InvitationToCompanyViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='company-invitation-list',
    ),
    path(
        '<int:company_pk>/invitations/<int:pk>/',
        InvitationToCompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='company-invitation-detail',
    ),

    path(
        '<int:company_pk>/requests/',
        RequestToCompanyViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='company-request-list',
    ),
    path(
        '<int:company_pk>/requests/<int:pk>/',
        RequestToCompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='company-request-detail',
    ),
]
