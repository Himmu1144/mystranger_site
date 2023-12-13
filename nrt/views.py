from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q

import json

from account.models import Account
# from chat.models import PrivateChatRoom, RoomChatMessage
from itertools import chain
from chat.utils import find_or_create_private_chat
from mystranger_app.models import Flags

from nrt.models import NrtPrivateChatRoom, NrtRoomChatMessage, AllActivatedUsers
from mystranger_app.models import University
import random


DEBUG = False


def nrt_text_view(request, *args, **kwargs):
    
    context = {}
    user = request.user

    if request.method == 'POST':

        # print(request.POST)
        try:
            activated_list = AllActivatedUsers.objects.get(pk=1)
        except AllActivatedUsers.DoesNotExist:
            activated_list = AllActivatedUsers.objects.create(pk=1)
            activated_list.save()
        
        if 'activate' in request.POST:
            # Handle Form 1 submission
            added = activated_list.add_user(user)
            print('added - ', added)
            context['status'] = True
            # return render(request, "nrt/nrt_text.html", context)

        elif 'deactivate' in request.POST:
            # Handle Form 2 submission
            removed = activated_list.remove_user(user)
            print('removed - ', removed)
            context['status'] = False

            ''' also have to remove this user from all the nrtrooms it is been a part of  '''
            NrtPrivateChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user)).delete()
            # return render(request, "nrt/nrt_text.html", context)

        return redirect('nrt-text')
    else:

        try:
            activated_list = AllActivatedUsers.objects.get(pk=1)
        except AllActivatedUsers.DoesNotExist:
            activated_list = AllActivatedUsers.objects.create(pk=1)
            activated_list.save()
        
        if user in activated_list.users.all():
            context['status'] = True

            ''' so now the user is that one which has already activated this feature, now we wanna check whether he/she is already joined with someone or not because if joined than show the chatroom if not than connect it with someone '''
            
            try:
                room = NrtPrivateChatRoom.objects.filter(Q(user1=user) | Q(user2=user) & Q(is_active=True)).first()
                if room:
                    # woah this user is a part of a room now we have to fetch its chats and messages show her/him
                    print('This use is a part already a part of the group handle it properly - ', room)
                    context['room'] = room
                    if room.user1 == request.user:
                        other_user_name = room.user2.name + ' | ' + room.user2.university_name
                    else:
                        other_user_name =  room.user1.name + ' | ' + room.user1.university_name

                    context['other_user_name'] = other_user_name
                    # return HttpResponse(f'you are already connected at this room - {room} ')
                else:
                    print('This user is not a part of any group')

                    # wut the room doesn't exist so now we gotta create one here 
                    ''' The user doesn't have any room so we are gonna fetch all the nearby activated users that are not grouped and connect this user with them '''

                    # first fetch all activated users and create a set of all nearby activated users

                    all_activated_users = activated_list.users.all() # these are all the activated users

                    print('all activated users - ', all_activated_users)
                    

                        # have to fetch all nearby users
                    university = University.objects.get(name=user.university_name)
                    all_nearby_users = university.allNearbyUsers.all()

                    print('all_nearby_users - ', all_nearby_users)

                    all_nearby_activated_users = set()

                    for kid in all_nearby_users:
                        if kid != request.user:
                            if kid in all_activated_users:
                                all_nearby_activated_users.add(kid)

                    # now we have all nearby activated users , now we want all of those users which are not currently a part of any group

                    print('all nearby activated users - ', all_nearby_activated_users)

                    all_ungrouped_nearby_activated_kids = set()

                    for kid in all_nearby_activated_users:
                        is_grouped = nrt_grouped_status(kid)
                        if not is_grouped:
                            all_ungrouped_nearby_activated_kids.add(kid)

                    print('all_ungrouped_nearby_activated_kids - ', all_ungrouped_nearby_activated_kids)

                    if len(all_ungrouped_nearby_activated_kids) == 0:
                        context['unavaillable'] = 'Sorry all other users are either already grouped or has not activated this feature yet try again later....'

                    else:
                        # now we have all the fucking ungrouped nearby activated students

                        other_stranger = get_random_user(list(all_ungrouped_nearby_activated_kids), request.user.gender)
                        print('The other stranger is this one - ', other_stranger)

                        # now we have selected the other stranger we want to create a chatroom of this user with the other stranger 

                        super_chat_room = NrtPrivateChatRoom(user1=request.user, user2=other_stranger)
                        super_chat_room.save()

                        print('This is the created room - ', super_chat_room)

                        # now the room is created and we have to through this room back to the ui (of current user)

                        context['room'] = super_chat_room
                        # return render(request, "nrt/nrt_text.html", context)

            except NrtPrivateChatRoom.DoesNotExist:
                print('error occured fetching nrtprivatechatroom')

            return render(request, "nrt/nrt_text.html", context)

        else:
            context['status'] = False
            return render(request, "nrt/nrt_text.html", context)
    
    return render(request, "nrt/nrt_text.html", context)



    # try:


    #     # Redirect them if not authenticated
    #     if not user.is_authenticated:
    #         return redirect("login")

    #     if room_id:
    #         try:
    #             room = PrivateChatRoom.objects.get(pk=room_id)
    #             context["room"] = room
    #         except PrivateChatRoom.DoesNotExist:
    #             return HttpResponse('The room you are trying to access does not exist.')

    #     # 1. Find all the rooms this user is a part of
    #     rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    #     rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    #     # 2. merge the lists
    #     rooms = list(chain(rooms1, rooms2))
    #     print(str(len(rooms)))

    #     """
    #     m_and_f:
    #         [{"message": "hey", "friend": "Mitch"}, {
    #             "message": "You there?", "friend": "Blake"},]
    #     Where message = The most recent message
    #     """
    #     m_and_f = []
    #     for room in rooms:
    #         # Figure out which user is the "other user" (aka friend)
    #         if room.user1 == user:
    #             friend = room.user2
    #         else:
    #             friend = room.user1

    #         '''
    #         Fetching all the unread messages send by the friend to me (in our room)
    #         '''

    #         unread_messages = RoomChatMessage.objects.filter(
    #             Q(room=room) & Q(user=friend) & Q(read=False))
    #         unread_messages_count = unread_messages.count()

    #         m_and_f.append({
    #             'unread_messages_count': unread_messages_count,
    #                 'friend': friend
    #         })

    #     context['m_and_f'] = m_and_f
    #     context['debug'] = DEBUG
    #     context['id'] = request.user.id
    #     context['debug_mode'] = settings.DEBUG
    # except Exception as e:
    #     print(e)
    return render(request, "nrt/nrt_text.html", context)

# Ajax call to return a private chatroom or create one if does not exist


# def create_or_return_private_chat(request, *args, **kwargs):
#     user1 = request.user
#     payload = {}
#     if user1.is_authenticated:
#         if request.method == "POST":
#             user2_id = request.POST.get("user2_id")
#             try:
#                 user2 = Account.objects.get(pk=user2_id, is_verified = True)
#                 chat = find_or_create_private_chat(user1, user2)
#                 payload['response'] = "Successfully got the chat."
#                 payload['chatroom_id'] = chat.id
#             except Account.DoesNotExist:
#                 payload['response'] = "Unable to start a chat with that user."
#     else:
#         payload['response'] = "You can't start a chat if you are not authenticated."
#     return HttpResponse(json.dumps(payload), content_type="application/json")


# def report_view(request, *args, **kwargs):

#     print('The flag view is called')
#     user = request.user

#     if not request.user.is_authenticated:
#         return redirect("login")

#     if request.POST:
#         try:
#             flag_user_id = request.POST.get('flag_user_id')
#             flag_user_name = request.POST.get('flag_user_name')
#             reason = request.POST.get('flag-reason')
            
#             account = Account.objects.get(pk=flag_user_id, is_verified = True)
            
#             flag_object = Flags.objects.filter(user=account, Flagger=user)
            
#             if flag_object.exists():
#                 response_data = {
#                     'status' : "Already Flagged",
#                     'message' : 'You have already flagged this User!'
#             }
#             else:
#                 account.flags = account.flags + 1
#                 account.save()
                
#                 flag = Flags(flag_user_id=flag_user_id, user=account,
# 							reason=reason, Flagger=user)
#                 flag.save()
#                 response_data = {
#                     'status' : 'Flagged',
# 					'message': 'This Person has been reported!'
# 				}

#         except Exception as e:
#             print('The flag exception is - ', str(e))
#             response_data = {
#                 'status' : 'error',
#                 'message': str(e),
#             }

#     return HttpResponse(json.dumps(response_data), content_type="application/json")


def nrt_grouped_status(kid):

    room = NrtPrivateChatRoom.objects.filter(Q(user1=kid) | Q(user2=kid) & Q(is_active=True)).first()
    if room:
        is_grouped = True
    else:
        is_grouped = False
    return is_grouped

def get_random_user(student_list, current_user_gender):

    try:

        # Split the student list into opposite and same gender lists
        opposite_gender_list = [student for student in student_list if student.gender != current_user_gender]
        same_gender_list = [student for student in student_list if student.gender == current_user_gender]

        # Determine the probability for opposite and same gender
        opposite_gender_probability = 0.7
        same_gender_probability = 0.3

        # Randomly select a user based on the probabilities
        if random.uniform(0, 1) < opposite_gender_probability and opposite_gender_list:
            selected_user = random.choice(opposite_gender_list)
        elif same_gender_list:
            selected_user = random.choice(same_gender_list)
        else:
            # If one of the lists is empty, select from the other
            selected_user = random.choice(student_list)

        return selected_user

    except Exception as e:
        print('The exception at fetching nrt user - ', str(e))
        return None

