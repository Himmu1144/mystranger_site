from django.urls import path

from account.views import (
	account_view,
    edit_account_view,
    # edit_pass_view,
    tokenSend,
    verify
    
)

app_name = 'account'

urlpatterns = [
	path('<user_id>/', account_view, name="view"),
    path('<user_id>/edit/', edit_account_view, name='edit'),
    # path('<user_id>/edit-pass/', edit_pass_view, name='edit-pass'),

	path('register/token/', tokenSend, name="token"),
    path('verify/<auth_token>' , verify , name="verify"),
]