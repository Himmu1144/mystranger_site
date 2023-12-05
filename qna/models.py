from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from notification.models import Notification
from mystranger.settings import domain_name
from django.db.models.signals import m2m_changed


class PublicChatRoom(models.Model):

	# Room title
	title 				= models.CharField(max_length=255, unique=False, blank=False,)
	question			= models.CharField(max_length=2005, unique=False, blank=False,)
	owner               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='PublicChatRoom')
	timestamp           = models.DateTimeField(auto_now_add=True)
	


	

	# all users who are authenticated and viewing the chat
	users 				= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="users who are connected to chat room.")

	def __str__(self):
		return self.question

	def ans_count(self):
		return self.answers.filter(parent=None).count()

	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			is_user_added = True
		elif user in self.users.all():
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return self.question


class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs

class PublicRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a PublicChatRoom
    """
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room                = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add=True)
    content             = models.TextField(unique=False, blank=False,)
    emoji = models.CharField(max_length=2)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)

    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content


class Answer(MPTTModel):
	question            = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE, related_name='answers')
	user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	content             = models.TextField(unique=False, blank=False,)
	# parent  			= models.ForeignKey('self',on_delete=models.CASCADE, null=True)
	parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
	timestamp 			= models.DateTimeField(auto_now_add=True)
	likes				= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="Likes", blank=True, related_name='likes')
	ans_reports				= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="Reports", blank=True, related_name='ans_reports')
	is_like_action = models.BooleanField(default=False, editable=False)
	is_report_action = models.BooleanField(default=False, editable=False)

	# set up the reverse relation to GenericForeignKey
	notifications		= GenericRelation(Notification)

	class MPTTMeta:
		order_insertion_by = ['timestamp']

	def add_like(self, user):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not user in self.likes.all():
			self.likes.add(user)
			self.save()
			is_user_added = True
		elif user in self.likes.all():
			is_user_added = True
		return is_user_added 


	def remove_like(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if user in self.likes.all():
			self.likes.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 
	
	def add_flag(self, user):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not user in self.ans_reports.all():
			self.ans_reports.add(user)
			self.save()
			is_user_added = True
		elif user in self.ans_reports.all():
			is_user_added = True
		return is_user_added 


	def remove_flag(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if user in self.ans_reports.all():
			self.ans_reports.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 


	def __str__(self):
		return self.content
	
	@property
	def get_cname(self):
		"""
		For determining what kind of object is associated with a Notification
		"""
		return "Answer"

@receiver(post_save, sender=Answer)
def create_notification(sender, instance, **kwargs):

	# Check if the instance was saved due to a like action
	if instance.is_like_action:
		
		# find a way to notify users if someone likes their answer
				
		return 
	
	if instance.is_report_action:
		
		# find a way to notify users if someone likes their answer
				
		return 

	
	if instance.parent:
		if instance.parent.user != instance.user:
			instance.notifications.create(
				target=instance.parent.user,
				from_user=instance.user,
				redirect_url=f"{domain_name}/pika/question/{instance.id}/",
				verb=f"{instance.user.name} replied at your question",
				content_type=instance,
			)
	else:
		if instance.user != instance.question.owner:
			instance.notifications.create(
				target=instance.question.owner,
				from_user=instance.user,
				redirect_url=f"{domain_name}/pika/question/{instance.id}/",
				verb=f"{instance.user.name} Answered at your question",
				content_type=instance,
			)
		


# Signal handler to set is_like_action to True when likes are changed
@receiver(m2m_changed, sender=Answer.likes.through)
def update_is_like_action(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        instance.is_like_action = True
        instance.save()

# Signal handler to set is_like_action to True when likes are changed
@receiver(m2m_changed, sender=Answer.ans_reports.through)
def update_is_report_action(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        instance.is_report_action = True
        instance.save()









