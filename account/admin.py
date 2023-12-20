from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import Account 
from account.models import AccountToken
from account.models import RegistrationError, deleted_account , Prompt



class AccountAdmin(UserAdmin):
	list_display = ('email','name','date_joined', 'last_login', 'is_admin','is_staff','is_verified','last_activity')
	search_fields = ('email','name',)
	readonly_fields=('id', 'date_joined', 'last_login')
	ordering = ['email']

	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()

class DeleteAccountAdmin(admin.ModelAdmin):
	list_display = ('email','timestamp')
	search_fields = ('email','name',)
	readonly_fields=('id', 'timestamp')
	ordering = ['timestamp']

	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()

class RegErrorAccountAdmin(admin.ModelAdmin):
	list_display = ('email','timestamp')
	search_fields = ('email','uni_name')
	readonly_fields=('id', 'timestamp')
	ordering = ['timestamp']

	filter_horizontal = ()
	list_filter = ()
	fieldsets = ()


admin.site.register(Account, AccountAdmin)
admin.site.register(AccountToken)
admin.site.register(RegistrationError,RegErrorAccountAdmin)
admin.site.register(deleted_account,DeleteAccountAdmin)
admin.site.register(Prompt)