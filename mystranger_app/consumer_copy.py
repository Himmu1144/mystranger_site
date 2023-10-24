from channels.generic.websocket import AsyncJsonWebsocketConsumer
from mystranger_app.utils import generateOTP
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from mystranger_app.models import WaitingArea, GroupConnect, Profile, University, UniversityProfile
from django.db.models import Q
import random
import json

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        """
        Called when the websocket is handshaking as part of initial connection.
        """

        # Here we are defining some essential instance variables
        self.group_name = None
        self.id = None
        

        print('Connect - ')
        await self.accept()

        # creating a user_profile for this user

        
        user = self.scope['user']
        university = user.university_name
        self.origin = user.origin
        print(self.origin)

        # Here we are creating a temporary profile of the user
        user1 = await create_user(self.channel_name,user)

        # ***************************************************************************************
        
        '''
        This is important to identify who has send a command to the front-end from the back-end.
        '''
        self.id = user1.id

        # Sending this id to the front-end so that we can use it further.

        await self.send_json(
            {  
                "my_id": self.id,   
            },
        )

        # ***************************************************************************************
        user1_channel = user1.channel_name
        print(f'user with id - {user1.id} is created! ')

        '''
        fetching the waiting area to check whether there is another request availlable or not
        '''

        # waiting_list = await fetching_waiting_list(university,self.origin)

        # Here we are fetching the count of either origin waiting List or the Nearby waiting list to check whether someone is waiting in the waiting list or not , so that if the count is zero we can add this user into the respective waiting list but of the count is not zero that means stranger is availlable therefore we are gonna connect this user with the stranger ,The count here gives the count for both origin wl and nearby wl

        count, users = await fetching_waiting_list_count(university,self.origin,user)
        # payload = json.loads(count)

        print("----------------------------------")
        print(count)
        # users is the set of all the availlable strangers waiting in the wl
        print(users)

        # if self.origin:
        #     count = payload['origin_count']
        #     users = payload['origin_users']
        # else:
        #     count = payload['nearby_count']
        #     users = payload['nearby_users']

        # count = payload['count']
        # users = payload['users']

        print(f'the count is - {count}')

        '''
        Declaring the current user to identify which user is which one.
        '''
       

        if count != None:
            if count != 0:
                
                # try:

                print('yes another request is availlable')
                # fetching random user from the set of availlable strangers and then removing that lucky stranger from the waiting list
                random_user = user_random(users)
                print(random_user,'^^^^^^^create_group^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                is_removed = await removing_user_from_waiting_list(random_user,self.origin)
                if is_removed:
                    print('wassup -----------------------------------------')
                    print(f'random user has been selected (random_user_id : {random_user}) and thus also removed from the waiting list.')
                random_user_channel = random_user.channel_name

                # except Exception as e:
                #     print('This is my exception',e)

                '''
                now we have two users availlable , user1_self who is seeking to connect with a stranger, user2_random who was patiently waiting in the waiting list to get connected with a stranger.

                Now we have to create a group with these two users so that they can chat with each other.
                '''

                group_name = await create_group(user1, random_user)
                random_user_name, random_user_id = await fetch_name(random_user)
                
                user1_self_name , user1_self_id = await fetch_name(user1)

                

                if group_name:

                    await self.send_json(
                        {
                            "status_user1": 'user1',
                            'user_id': self.id,
                            'stranger' : random_user_name,
                        },
                    )

                    print(f'model group is created! {group_name}')

                    # Adding user1 to a group named group_name

                    try:
                        await self.channel_layer.group_add(
                            str(group_name),
                            str(user1_channel)
                        )
                    except Exception as e:
                        print(f'Execption in adding the users to the group - {e} ')
                        
                    print(f'user1 channel - {user1_channel}')

                    #  Adding user2_random to a group named group_name

                    try:
                        await self.channel_layer.group_add(
                            str(group_name),
                            str(random_user_channel)
                        )
                    except Exception as e:
                        print(f'Execption in adding the users to the group - {e} ')

                    print(f'random user channel - {random_user_channel}')


                    print('django channels group is created!')

                    '''
                    Here we are sending a message to the group, informing both the users that now they are connected with a stranger and can chat with each other.
                    '''
                    
                    # we have to check that why the fuck he is not sending message to the group, and even if he is sending than why it is not showing in the console.
                    
                    print(f'sending message to this group - {str(group_name)}')

                    try:
                        await self.channel_layer.group_send(
                            str(group_name),
                            {
                                "type": "joined.room",
                                "grouped": group_name,
                                "user1_self" : user1.id,
                                'random_user' : random_user.id,
                                'user1_self_name' : user1_self_name,
                                "user1_self_id" : user1_self_id,
                                'random_user_name' : random_user_name,
                                'random_user_id' : random_user_id,
                                'response' : 'You are now connected with a stranger.',
                            }
                        )
                    except Exception as e:
                        print(f'Execption in sending msg to the group - {e} ')

                    # await self.send_json(
                    #     {
                            
                    #         "test": 'yup got the test message.' ,
                            
                    #     },
                    # )

                    print('message about group creation has been sent!')

                else:
                    print('something went wrong and the group model is not created!')

            elif (count == 0):
                '''
                here this means that though the waiting area exists but there is no user waiting in the waiting area thus therefore we are going to add this user to the waiting list so that it can get connected with others.
                '''
                print('adding user to the waiting area by fetching the waiting area.')
                waiting_list = await create_waiting_list_and_add_user(user1,self.origin)
                print(f'random_user_channel - {user1_channel}')
                await self.send_json(
                {
                    "status_user2": 'random_user',
                    'user_id': self.id,
                },
            )

            else:
                print('There is some problem with the waiting list users count.')

        else:
            '''
            this means that waiting list doesn't exist thus we can't connect user1 with any random user and hence we have to add user1 into the waiting list so that it can be added by others.
            '''
            print('adding user to the waiting area by creating a waiting area.')
            waiting_list = await create_waiting_list_and_add_user(user1,self.origin)
            print(f'random_user_channel - {user1_channel}')
            await self.send_json(
                {
                    "status_user2": 'random_user',
                    'user_id': self.id,
                },
            )


    # --------------------------------------------------------------------------------

    async def receive_json(self, content):

        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """

        command = content.get("command", None)
        print("receive_json: " + str(command) , 'id : ' + str(self.id))

        try:
            if command == 'grouped':
                self.group_name = content['group_name']
                print(f'instance variable self.group_name has been set for {self.id} ')
            elif command == 'send':
                await self.send_room(content["group_name"], content['user_id'], content["message"])
            elif command == 'skip':
                group_name = content['group_name']
                if group_name:
                    print('command : skip | the group does exist!')
                    await self.channel_layer.group_send(
                    group_name,
                    {
                        "type": "leave.room",
                        'by_skip' : 'skip',
                        'leave': 'Chat Disconnected',
                        'disconnector' : self.id,
                        'response' : 'You are no longer connected with the stranger.',
                    }
                )
                else :
                    print('command : skip | the group does not exist!')
                    user = await fetch_user(self.id)
                    is_removed = await removing_user_from_waiting_list(user, self.origin)
                    print(f'user - {self.id} is removed from wl - {is_removed}')
                    await self.send_json(
                        {
                            'leave': 'Chat Disconnected',
                            'disconnector' : self.id,
                            'response' : 'You are no longer connected with the stranger.',
                        },
                    )  
            elif command == 'offer':
                await self.channel_layer.group_send(content['group'],{
                'type':'offer.message',
                'offer':content['offer']
            })
            elif command == 'answer':
                await self.channel_layer.group_send(content['group'],{
                'type':'answer.message',
                'answer':content['answer']
            })
            elif(content['command'] == 'candidate'):
                await self.channel_layer.group_send(content['group'],{
                    'type':'candidate.message',
                    'candidate':content['candidate'],
                    'iscreated':content['iscreated']
                })
        
                
        except Exception as e:
            print(e)

    # --------------------------------------------------------------------------------

    async def disconnect(self, code):

        if self.group_name:


            print('group_name in Diconnect Function')

        
            user_self = await fetch_user(self.id)
            if user_self:

                print('Discarding the group')

                group_obj = await fetch_group(user_self)
                group_dict = await group_info(group_obj)
                group_name =  group_dict['group_name']


            
                user1_channel = group_dict['user1_channel']
                user1_id = group_dict['user1_id']
                random_user_channel = group_dict['random_user_channel']
                random_user_id = group_dict['random_user_id']
                

                # But before that we have to notify in the group that it has been discarded.

                await self.channel_layer.group_send(
                    str(group_name),
                    {
                        "type": "leave.room",
                        'leave': 'Chat Disconnected',
                        'by_skip' : 'normal',
                        'disconnector' : self.id,
                        'response' : 'You are no longer connected with the stranger.',
                    }
                )

                # Discarding both the users from the group named group_name

                # Discarding User1 from the group
                print(f'Discarding {user1_channel} from the group.')
                await self.channel_layer.group_discard(
                    str(group_name),
                    str(user1_channel)
                )

                # Discarding random_user from the group
                print(f'Discarding {random_user_channel} from the group.')
                await self.channel_layer.group_discard(
                    str(group_name),
                    str(random_user_channel)
                )

                # Deleting both the users

                # Deleting User1
                print(f'deleting user1 - {user1_id}')
                user1_deleted = await delete_user(user1_id)
                print(f'Status : ' + str(user1_deleted))

                # Deleting random_user
                print(f'deleting random_user - {random_user_id}')
                random_user_deleted = await delete_user(random_user_id)
                print(f'Status : ' + str(random_user_deleted))

                self.group_name = None

            else:

                '''
                This means that the group has already been discarded beacuse both the uers have already been deleted.
                therefore here we have to do nothing.
                '''

                print('Just chill group has already been discarded.')
                self.group_name = None
        
        else:

            '''
            This means that there is no group formed and the user is simply trying to skip without creating a group. Therefore we just have to delete this user and by deleting it , the user is also automatically gonna get removed from the waiting list.
            '''

            print(f'user - {self.id} deleted!')
            await self.send_json(
                {
                    'leave': 'Chat Disconnected',
                    'disconnector' : self.id,
                    'response' : 'You are no longer connected with the stranger.',
                },
            )

            delete_user_self = await delete_user(self.id)
            print(f'Status : {delete_user_self}')
            self.id = None

            


    # --------------------------------------------------------------------------------


    async def joined_room(self, event):

        await self.send_json(
            {
                "grouped": event['grouped'],
                "user1": event["user1_self"],
                "user1_self_name": event["user1_self_name"],
                "user1_self_id": event["user1_self_id"],
                "random_user_name": event["random_user_name"],
                "random_user_id": event["random_user_id"],
                "random_user": event["random_user"],
                "response": event["response"],
            },
        )

    async def leave_room(self, event):
        await self.send_json(
            {
                "leave": event['leave'],
                'by_skip' : event['by_skip'],
                'disconnector': event['disconnector'],
                "response": event["response"],
                
            },
        )

    # --------------------------------------------------------------------------------

    async def send_room(self, group_name, user_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """

        print("-----------  send_room  ---------------\n")
        print('The group name is - ', group_name)
        print("user : " + str(user_id))
        print("message : " + message)
        print("----------------------------------------\n")


        await self.channel_layer.group_send(
            str(group_name),
            {
                "type": "chat.message",
                'id': user_id,
                "message": message,
            }
        )

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(
            {
                "msg_type": 0,
                'id': event['id'],
                "message": event["message"],
            },
        )
    
    # --------------------------------------------------------------------------------

    async def offer_message(self,event):
        await self.send_json({
            'command':'offer',
            'offer':event['offer']
        })

    async def answer_message(self,event):
        await self.send_json({
            'command':'answer',
            'answer':event['answer']
        })

    async def candidate_message(self,event):
        await self.send_json({
            'command':'candidate',
            'candidate':event['candidate'],
            'iscreated':event['iscreated']
        })
    

# Writing functions to fetch data from database through database_sync_to_async context
# ------------------------------------------------------------------------------------

'''
Creating a User with username as channel_layer of that user and pk is a random 8 digit code to make the user_id unique. 
Right now we are using default User Model therefore we have to store the channel_layer as the username later on we are gonna create a more solid user_profile.
'''

@database_sync_to_async
def create_user(channel_name,user):
    id = generateOTP()
    channel = str(channel_name)
    user = user
    profile = Profile(id=id,channel_name=channel,user=user)
    profile.save()
    return profile

@database_sync_to_async
def fetch_profile_id(profile):
    return profile.user.id


@database_sync_to_async
def delete_user(id):
    try:
        profile = Profile.objects.get(id=id)
        profile.delete()
        deleted = True
    except:
        deleted = False
    return deleted

# ----------------------------------------------------------------------------------------

'''
Here we are fetching the waiting list, assuming that it has already been created with pk equals to 1.
'''

@database_sync_to_async
def fetching_waiting_list(university_name,origin):

    # try:
    #     waiting_list = WaitingArea.objects.get(pk=1)
    #     if origin:
    #         users = waiting_list.users.filter(user__university_name=university_name)
    #         if users:
    #             return waiting_list
    # except:
    #     waiting_list = None

    # This means we are dealing with users of nearby

#----------------------------------------------------------------------------------

    try:
        waiting_list = None
        if origin:
            # This means we are dealing with users of origin
            waiting_list = WaitingArea.objects.get(pk=1)
            if waiting_list:
                return waiting_list
        else:
            waiting_list = WaitingArea.objects.get(pk=2)
            if waiting_list:
                return waiting_list
    except WaitingArea.DoesNotExist:
        waiting_list = None

    return waiting_list


'''
here we are fetching the waiting list , assuming that it has already been created with pk equals to 1, 
after that we are returning the count of all the users present in the waiting list to make sure that the list isn't empty.
'''

@database_sync_to_async
def fetching_waiting_list_count(university_name,origin,auth_user):

    # try:
    #     waiting_list = WaitingArea.objects.get(pk=1)
    #     # need some work
    #     # users = waiting_list.users.filter(user__university_name=university_name)
    #     users = waiting_list.users.all()
    #     if waiting_list and users:
    #         count = users.count()
    #     else:
    #         count = 0
    # except:
    #     count = 0

    try:
        count = None
        if origin:
            # This means we are dealing with users of origin
            waiting_list = WaitingArea.objects.get(pk=1)
            waiting_list_nearby = WaitingArea.objects.get(pk=2)
            users_nearby = waiting_list_nearby.users.filter(user__university_name=university_name)
            set1 = set(users_nearby)

            # we need the count of all the users from origin that are from his university
            users = waiting_list.users.filter(user__university_name=university_name)
            set2 = set(users)
            if waiting_list and (users.exists() or users_nearby.exists()):
                count1 = users.count()
                count2 = users_nearby.count()
                count = count1 + count2
            set3 = set1.union(set2)
            # payload = {'count' : count, 'users' : list(users)}
            # return json.dumps(payload)
            print("The Origin count ------",count)
            print("The set ------",set3)
            return count , set3
        else:
            
            waiting_list = WaitingArea.objects.get(pk=2)
            
            # we need the count of all the users from origin that are from his university plus all the users from wl that are in his nearby_list
            waiting_list_origin = WaitingArea.objects.get(pk=1)
            users = waiting_list_origin.users.filter(user__university_name=university_name)
            print(users)
            users_nearby = waiting_list.users.filter(user__university_name=university_name)
            print(users_nearby)
            set1_1 = set(users)
            print("set 1_1 -------", set1_1)
            set1_2 = set(users_nearby)
            print("set 1_2 -------", set1_2)
            set1 = set1_1.union(set1_2)
            print("set 1 -------", set1)
            all_nearby_users = University.objects.none()
            try:    
                university = University.objects.get(name=university_name)
                print('Uni exists so no profile dwelling')
                nearby_universities = university.nearbyList.all()
                print("These are the nearby universities list - ",nearby_universities)

                # --------------------------------------------------------------------------------------------
                # right now if a user with uni_prof is here then it can only connect with others by fetching the other user but other users can't fetch him so if he is in the waiting list then he is not going to get connected with anyone and that's how it is , although we can fix that by adding all_nearby_users_from_profiles but we are not going to do that.

                for universiti in nearby_universities:
                    all_nearby_users |= universiti.users.all()
                
                # all_nearby_users = list(all_nearby_users)
                all_nearby_users_list = []
                for obj in all_nearby_users:
                    all_nearby_users_list.append(obj.email) 

                # for obj in all_nearby_users_list:
                #     print(obj)
                #     if 'himanshu.20scse1010435@galgotiasuniversity.edu.in' == obj.email:
                #         print('Yup true')
                #     else:
                #         print('Sup false')
                # if 'himanshu.20scse1010435@galgotiasuniversity.edu.in' in all_nearby_users_list:
                #     print('yes you fuckin hell')
                print("All nearby users -----", all_nearby_users_list)

                nearby_waiting_list_users = waiting_list.users.all()
                print('These are all the nearby waiting list users - ', nearby_waiting_list_users)
                set2 = set()
                for user in nearby_waiting_list_users:
                    print("user from nwlu - ", user.user.email, type(user.user.email))
                    if user.user.email in all_nearby_users_list:
                        print("Yes this brat is in the all_nearby_users",user.user)
                        set2.add(user)
            except University.DoesNotExist:
                print('Uni does not exist so profile dwelling')

                university_prof = UniversityProfile.objects.filter(Q(name=university_name) & Q(users=auth_user)).first()
                print('The university profile is ---------', university_prof)

                nearby_universities = university_prof.nearbyList.all()
                print("These are the nearby universities list - ",nearby_universities)

                for universiti in nearby_universities:
                    all_nearby_users |= universiti.users.all()
                
                all_nearby_users_list = []
                for obj in all_nearby_users:
                    all_nearby_users_list.append(obj.email) 

                print("All nearby users -----", all_nearby_users_list)

                nearby_waiting_list_users = waiting_list.users.all()
                print('These are all the nearby waiting list users - ', nearby_waiting_list_users)
                set2 = set()
                
                for user in nearby_waiting_list_users:
                    if user.user.email in all_nearby_users_list:
                        print("Yes this brat is in the all_nearby_users",user.user)
                        set2.add(user)

            print("Set2 ------------",set2)
            set3 = set1.union(set2)
            print("Set3 ------------",set3)
            if waiting_list and (len(set3)!=0):
                count = len(set3)
            # payload = {'count':count,'users' : list(set3)}
            # return json.dumps(payload)
            print("The Nearby count ------",count)
            print("The set ------",set3)
            return count , set3
           
    # except WaitingArea.DoesNotExist:
    except Exception as e:
        print("The fucking exception in count - ",str(e))
        # payload = {'count' : None,'users':None}
        count = None
        set3 = None
    print("The default count ----",count)
    print("The set ------",set3)
    return count , set3 
    
# ----------------------------------------------------------------------------------------

'''
here assuming that we have fetched the waiting list and the list isn't empty, therefore we are fetching a random user from the waiting list.
'''

# def get_random_user(users):
#     random_user = random.choice(list(users))
#     return random_user


# @database_sync_to_async
# def user_random(university_name, origin):
#     try:
#         waiting_list = WaitingArea.objects.get(pk=1)
#         if origin:
#             users = waiting_list.users.filter(user__university_name=university_name)
#             if users.exists():
#                 users = set(users)
#                 print(users,'chupa :::::::::::::::::::::::::::::::')
#                 random_user = random.choice(list(users))
#                 print(random_user)

#             else:
#                 random_user = 'Mai Chutiya hoon'
#         else:
#             '''
#             This means that the user is using the nearby option thus we have to select a random user from the list of all the users that belongs to the Nearby list of user1 + users of its own university and have also the same nearby setting
#             '''

#             users = waiting_list.users.filter(Q(user__university_name=university_name))
#             if users.exists():
#                 users = set(users)
#             else:
#                 users = set()

#             print(users,'llllllllllllllllllllllll')
#             all_waiting_users = waiting_list.users.all()
#             print(all_waiting_users,'3333333333333333333333333333333333333')
#             all_nearby_users = University.objects.none()
#             university = University.objects.get(name=university_name)
#             nearby_universities = university.nearbyList.all()
#             for university in nearby_universities:
#                 all_nearby_users |= university.users.all()

#             print(all_nearby_users, '**********************************')

#             # Thus the users is gonna contain a query set which has all the users from the current university and all the nearby universities of that current university

#             for user in all_waiting_users:
#                 if user.user in all_nearby_users and user.user.origin == False:
#                     users.add(user)

#             print(users,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
#             if users:
#                 random_user = random.choice(list(users))
#             else:
#                 random_user = 'Maybe'

#     except Exception as e:
#         print('exception - ', e)
#         return 'Jaadu'
#     return random_user


def user_random(setva):
    random_user = random.choice(list(setva))
    return random_user

# ----------------------------------------------------------------------------------------

'''
simple function to remove a user from the waiting list.
'''

@database_sync_to_async
def removing_user_from_waiting_list(user,origin):

    # try:
    #     waiting_list = WaitingArea.objects.get(pk=1)
    #     if waiting_list:
    #         is_removed = waiting_list.remove_user(user)
    # except:
    #     is_removed = False

    try:
        if origin:
            # This means we are dealing with users of origin
            waiting_list = WaitingArea.objects.get(pk=1)
            if waiting_list:
                is_removed = waiting_list.remove_user(user)
        else:
            waiting_list = WaitingArea.objects.get(pk=2)
            if waiting_list:
                is_removed = waiting_list.remove_user(user)
    except WaitingArea.DoesNotExist:
        waiting_list = None
    return is_removed

# ----------------------------------------------------------------------------------------

'''
simple function to create a group of two users.
'''

@database_sync_to_async
def create_group(user1, user2):
    group_name = GroupConnect.objects.create(user1=user1, user2=user2)
    return str(group_name)

# ----------------------------------------------------------------------------------------

'''
Here we are adding the user to the waiting list by either creating the waiting list or by fetching the existimg waiting list.
'''

@database_sync_to_async
def create_waiting_list_and_add_user(user,origin):

    # try:
    #     waiting_list = WaitingArea.objects.get(pk=1)
    #     if waiting_list:
    #         is_added = waiting_list.add_user(user)
    # except:
    #     waiting_list = WaitingArea.objects.create(pk=1)
    #     is_added = waiting_list.add_user(user)

    if origin:
        try:
            waiting_list = WaitingArea.objects.get(pk=1)
            if waiting_list:
                is_added = waiting_list.add_user(user)
        except:
            waiting_list = WaitingArea.objects.create(pk=1)
            is_added = waiting_list.add_user(user)
    else:
        try:
            waiting_list = WaitingArea.objects.get(pk=2)
            if waiting_list:
                is_added = waiting_list.add_user(user)
        except:
            waiting_list = WaitingArea.objects.create(pk=2)
            is_added = waiting_list.add_user(user)
    return is_added

# ----------------------------------------------------------------------------------------


'''
Here we are fetching the group_name by using a user.
'''

@database_sync_to_async
def fetch_group(user):
    try:
        group_name = GroupConnect.objects.get(Q(user1=user) | Q(user2=user))
    except:
        group_name = None
    return group_name


'''
Here we are fetching a user by using it's id
'''

@database_sync_to_async
def fetch_user(id):
    try:
        user = Profile.objects.get(pk=id)
    except:
        user = None
    return user


# ----------------------------------------------------------------------------------------

'''
Here we are creating a function so that we can fetch the groups info, if we have a group instance
'''

@database_sync_to_async
def group_info(group):

    group_obj = group

    user1_channel = group_obj.user1.channel_name
    user1_id = group_obj.user1.id
    random_user_channel = group_obj.user2.channel_name
    random_user_id = group_obj.user2.id

    group_dict = {
        'group_name' : str(group_obj),
        'user1_channel': user1_channel,
        'user1_id' : user1_id,
        'random_user_channel' : random_user_channel,
        'random_user_id' : random_user_id
    }

    return group_dict

@database_sync_to_async
def fetch_name(profile):
    name = profile.user.name
    id = profile.user.id
    return name , id
