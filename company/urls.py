from django.urls import path

from user.views import RequestToCompanyViewSet

from .views import CompanyViewSet, InvitationToCompanyViewSet

urlpatterns = [
    path('', CompanyViewSet.as_view({'get': 'list', 'post': 'create'}), name='company-list'),
    path(
        '<int:pk>/',
        CompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='company-detail',
    ),
    path('<int:pk>/members/', CompanyViewSet.as_view({'get': 'members'}), name='company-members'),
    path('<int:company_pk>/admins/', CompanyViewSet.as_view({'get': 'admins'}), name='company-admins'),
    path(
        '<int:company_pk>/appoint_admin/<int:pk>/',
        CompanyViewSet.as_view({'post': 'appoint_admin'}),
        name='company-appoint-admin'
    ),
    path(
        '<int:company_pk>/remove_admin/<int:pk>/',
        CompanyViewSet.as_view({'post': 'remove_admin'}),
        name='company-remove-admin'
    ),
    path('<int:pk>/remove_me/', CompanyViewSet.as_view({'delete': 'remove_me'}), name='company-remove-me'),
    path(
        '<int:company_pk>/remove_user/<int:pk>/',
        CompanyViewSet.as_view({'delete': 'remove_user'}),
        name='company-remove-user',
    ),

    path(
        '<int:company_pk>/invitations/',
        InvitationToCompanyViewSet.as_view({'get': 'list'}),
        name='company-invitation-list',
    ),
    path(
        '<int:company_pk>/invitations/<int:pk>/',
        InvitationToCompanyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'post': 'create'}),
        name='company-invitation-detail',
    ),
    path(
        '<int:company_pk>/invitations/<int:pk>/revoke/',
        InvitationToCompanyViewSet.as_view({'post': 'revoke'}),
        name='company-invitation-revoke',
    ),

    path('<int:company_pk>/requests/', RequestToCompanyViewSet.as_view({'get': 'list'}), name='company-request-list'),
]
