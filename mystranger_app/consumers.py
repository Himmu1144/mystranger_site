from channels.generic.websocket import AsyncJsonWebsocketConsumer
from mystranger_app.utils import generateOTP
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from mystranger_app.models import WaitingArea, GroupConnect
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

        

        user1 = await create_user(self.channel_name)
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
        user1_channel = user1.username
        print(f'user with id - {user1.id} is created! ')

        '''
        fetching the waiting area to check whether there is another request availlable or not
        '''

        waiting_list = await fetching_waiting_list()
        count = await fetching_waiting_list_count()
        print(f'the count is - {count}')

        '''
        Declaring the current user to identify which user is which one.
        '''
       

        if waiting_list:
            if count != 0:

                print('yes another request is availlable')
                random_user = await user_random()
                is_removed = await removing_user_from_waiting_list(random_user)
                if is_removed:
                    print(f'random user has been selected (random_user_id : {random_user.id}) and thus also removed from the waiting list.')
                random_user_channel = random_user.username

                '''
                now we have two users availlable , user1_self who is seeking to connect with a stranger, user2_random who was patiently waiting in the waiting list to get connected with a stranger.

                Now we have to create a group with these two users so that they can chat with each other.
                '''

                group_name = await create_group(user1, random_user)

                if group_name:
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
                waiting_list = await create_waiting_list_and_add_user(user1)
                print(f'random_user_channel - {user1_channel}')

            else:
                print('There is some problem with the waiting list users count.')

        else:
            '''
            this means that waiting list doesn't exist thus we can't connect user1 with any random user and hence we have to add user1 into the waiting list so that it can be added by others.
            '''
            print('adding user to the waiting area by creating a waiting area.')
            waiting_list = await create_waiting_list_and_add_user(user1)
            print(f'random_user_channel - {user1_channel}')


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
                    is_removed = await removing_user_from_waiting_list(user)
                    print(f'user - {self.id} is removed from wl - {is_removed}')
                    await self.send_json(
                        {
                            'leave': 'Chat Disconnected',
                            'disconnector' : self.id,
                            'response' : 'You are no longer connected with the stranger.',
                        },
                    )  
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


# Writing functions to fetch data from database through database_sync_to_async context
# ------------------------------------------------------------------------------------

'''
Creating a User with username as channel_layer of that user and pk is a random 8 digit code to make the user_id unique. 
Right now we are using default User Model therefore we have to store the channel_layer as the username later on we are gonna create a more solid user_profile.
'''

@database_sync_to_async
def create_user(channel_name):
    id = generateOTP()
    username = str(channel_name)
    password = id
    user = User.objects.create_user(
        pk=id, username=username, password=password)
    user.save()
    return user


@database_sync_to_async
def delete_user(id):
    try:
        user = User.objects.get(id=id)
        user.delete()
        deleted = True
    except:
        deleted = False
    return deleted

# ----------------------------------------------------------------------------------------

'''
Here we are fetching the waiting list, assuming that it has already been created with pk equals to 1.
'''

@database_sync_to_async
def fetching_waiting_list():

    try:
        waiting_list = WaitingArea.objects.get(pk=1)
    except:
        waiting_list = None

    return waiting_list


'''
here we are fetching the waiting list , assuming that it has already been created with pk equals to 1, 
after that we are returning the count of all the users present in the waiting list to make sure that the list isn't empty.
'''

@database_sync_to_async
def fetching_waiting_list_count():

    try:
        waiting_list = WaitingArea.objects.get(pk=1)
        if waiting_list:
            count = waiting_list.users.through.objects.count()
    except:
        count = None

    return count
    
# ----------------------------------------------------------------------------------------

'''
here assuming that we have fetched the waiting list and the list isn't empty, therefore we are fetching a random user from the waiting list.
'''

@database_sync_to_async
def user_random():
    try:
        waiting_list = WaitingArea.objects.get(pk=1)
        users = waiting_list.users.all()
        if users:
            random_user = random.choice(users)
        else:
            random_user = None
    except WaitingArea.DoesNotExist:
        return None
    return random_user

# ----------------------------------------------------------------------------------------

'''
simple function to remove a user from the waiting list.
'''

@database_sync_to_async
def removing_user_from_waiting_list(user):

    try:
        waiting_list = WaitingArea.objects.get(pk=1)
        if waiting_list:
            is_removed = waiting_list.remove_user(user)
    except:
        is_removed = False

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
def create_waiting_list_and_add_user(user):

    try:
        waiting_list = WaitingArea.objects.get(pk=1)
        if waiting_list:
            is_added = waiting_list.add_user(user)
    except:
        waiting_list = WaitingArea.objects.create(pk=1)
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
        user = User.objects.get(pk=id)
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

    user1_channel = group_obj.user1.username
    user1_id = group_obj.user1.id
    random_user_channel = group_obj.user2.username
    random_user_id = group_obj.user2.id

    group_dict = {
        'group_name' : str(group_obj),
        'user1_channel': user1_channel,
        'user1_id' : user1_id,
        'random_user_channel' : random_user_channel,
        'random_user_id' : random_user_id
    }

    return group_dict


                

