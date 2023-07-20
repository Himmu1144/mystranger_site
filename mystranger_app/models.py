from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from mystranger_app.utils import calculate_distance


'''
universities model which contain all the universities inside it and each university contain all the users of that particular university inside them.
'''

class University(models.Model):

    name = models.CharField(max_length=100, unique=True, blank=False)
    universityName = models.CharField(max_length=150, blank=False)
    universityAddress = models.CharField(max_length=1000, blank=True)
    lat = models.FloatField(blank=False)
    lon = models.FloatField(blank=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=("users"), blank=True)
    nearbyList = models.ManyToManyField('self', verbose_name=("nearby_universities"), blank=True) 

    def add_user(self, account):
        """
        Add a new friend.
        """
        if not account in self.users.all():
            self.users.add(account)
            self.save()

    def __str__(self):
        return self.name
    
'''
Profiles which are going to be used as temporary users inside the consumer, while connecting with a stranger each user is going to have their own unique profile which is going to act as them.
'''

class Profile(models.Model):

    id = models.IntegerField(primary_key=True)
    channel_name = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.name} - {self.id}' 
    

'''
Creating waiting area that takes profiles as users 
'''

class WaitingArea(models.Model):

    users = models.ManyToManyField(Profile, verbose_name=("waiting-users"), blank=True)

    def add_user(self, user):
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


    def remove_user(self, user):
        """
        return true if user is removed from the users list
        """
        is_user_removed = False
        if user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True
        return is_user_removed 

    def __str__(self):
        return 'waiting list'
    

class GroupConnect(models.Model):
    user1 = models.ForeignKey(Profile, verbose_name="User_1", related_name='user_1' , on_delete=models.CASCADE)
    user2 = models.ForeignKey(Profile, verbose_name="User_2", related_name='user_2' , on_delete=models.CASCADE)

    def group_name(self,user1,user2):
        return f'{self.user1.id}{self.user2.id}'

    def __str__(self):
        return f'{self.user1.id}{self.user2.id}'
    
'''
Creating University profile, these profiles are going to be used as a temporary university untill someone verifies and created the actual university from the backend.
'''

class UniversityProfile(models.Model):

    name = models.CharField(max_length=100, blank=False)
    universityName = models.CharField(max_length=150, blank=False)
    universityAddress = models.CharField(max_length=1000, blank=True)
    lat = models.FloatField(blank=False)
    lon = models.FloatField(blank=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=("users"), blank=True)
    nearbyList = models.ManyToManyField(University, verbose_name=("nearby_universities"), blank=True) 
    verified = models.BooleanField(default=False)



    def add_user(self, account):
        """
        Add a new friend.
        """
        if not account in self.users.all():
            self.users.add(account)
            self.save()
    
    def users_count(self):
        return self.users.count()

    def __str__(self):
        return self.name
    
@receiver(post_save, sender=UniversityProfile)
def _post_save_receiver_for_profile(sender, instance, **kwargs):
    verified = instance.verified
    if verified:
        uni_email = instance.name
        all_uni_prof = UniversityProfile.objects.filter(name=uni_email)
        
        university = University(name=instance.name,lat=instance.lat,lon=instance.lon)
        university.universityName = instance.universityName
        university.save()
        nearby_list = []
        universities = University.objects.all()
        
        # nearby_list = instance.nearbyList.all()
        # university.nearbyList.add(*nearby_list)
        # university.save()

        nearby_list = []
        universities = University.objects.all()
        for uni in universities:
            Lat1 = uni.lat
            Lon1 = uni.lon

            distance = calculate_distance(instance.lat, instance.lon, Lat1, Lon1)
            if distance <= 60:
                '''
                This means that yes this uni lies with in 60 km of registration uni
                '''
                nearby_list.append(uni)

        university.nearbyList.add(*nearby_list)
        university.save()

        for uni in nearby_list:
            uni.nearbyList.add(university)
            uni.save()
        
        for prof in all_uni_prof:
            prof_uesrs = prof.users.all() 
            university.users.add(*prof_uesrs)

        '''
        This below code gives an error becuase we can't delete all the profs in a profs post save therefore we have to find some another way to delete all profs when one prof is verified and converted into university model
        '''
        # all_uni_profs = UniversityProfile.objects.filter(name=university.name)
        # if all_uni_profs.exists():
        #     for prof in all_uni_profs:
        #         prof.delete()

        university.save()


