from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from mystranger_app.models import University , UniversityProfile


class RegisterConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):

        """
        Called when the websocket is handshaking as part of initial connection.
        """

        print('Connect - ')
        await self.accept()

        await self.send_json({
            'connected': 'you are now connected with the consumer'
        },)

    async def receive_json(self, content):

        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """

        command = content.get("command", None)
        print("receive_json: " + str(command))

        try:
            if command == 'email':
                await self.send_info(content["email_address"])
        except Exception as e:
            print(e)

    async def disconnect(self, code):
        pass

    async def send_info(self, email):
        """
        Called by receive_json when someone sends a message to a room.
        """

        # going to write the logic here

        '''
        first we will check that do we have a university associated with that email or not.
        '''
        university = None
        lat = None 
        lon = None
        uniprofile = False
        fetched_from = None

        print('Everything at None - Just starting')

        try:
            name = email.split('@')[-1:][0]
            university = await fetch_university(name)
            # fetching university from university models
            if university:
                lat = university.lat
                lon = university.lon
                university = university.universityName
                fetched_from = 0

                print('fetched from - 0 , found on existing universities')
            else:
                '''
                This means that we don't have any university associated with the given email, therefore we are now going to look into our database to check whether we have any university in our database that is associated with this email.
                '''

                universities_database = {
                    "gn.amity.edu": ["Amity University, Greater Noida", 28.54322285, 77.33274829733952],
                    "galgotiasuniversity.edu.in": ["Galgotias University", 28.3671232, 77.54045993787369],
                    "bennett.edu.in": ["Bennett University", 28.450610849999997, 77.58391181955102],
                    "sharda.ac.in": ["Sharda University", 28.4734073, 77.4829339],
                    "niu.edu.in": ["Noida International University", 28.37390315, 77.54131056418103],
                    "cu.edu.in": ["Chandigarh University", 30.7680079, 76.57566052483162],
                }

                

                try:
                    if name in universities_database:
                        info = universities_database[name]
                        university = info[0]
                        lat = info[1]
                        lon = info[2]
                        fetched_from = 2

                        print('Using The Json Database')

                    else: 
                        '''
                        This means that the given university doesn't exist in our database therefore we need to take this university as an input from the user.
                        
                        - but first we are gonna check whether there is a profile for that university or not , and if there are many profiles then the profile with the maximum user is going to get selected.

                        - though we still don't know for sure that whether this profile is true or not. therefore we are going to give user an option saying not my university and by clicking on that user can input their university through search Map.
                        '''

                        university = await fetch_university_profile(name=name)
                        print('looking inside profiles')

                        if university:
                            lat = university.lat
                            lon = university.lon
                            university = university.universityName
                            uniprofile = True
                            fetched_from = 1

                        else:
                            print('Only Option is to take user input')
                            fetched_from = 'nope'
                            university = 'nope'
                        
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

        await self.send_json(
            {
                'fetched_from' : fetched_from,
                'universityName': str(university),
                'lat': lat,
                'lon': lon,
            },
        )

        if uniprofile:
            await self.send_json(
            {
                'trust_button' : 'Not My University'
            },
        )


'''
Some Functions to make our life easier.
'''


@database_sync_to_async
def fetch_university(name):
    try:
        university = University.objects.get(name=name)
    except University.DoesNotExist:
        university = None
    return university

'''
This function has to return all the uniprofiles and return the profile which has the maximum users in it.
'''

@database_sync_to_async
def fetch_university_profile(name):
    try:
        university_queryset = UniversityProfile.objects.filter(name=name)
        if university_queryset.exists():
            university_count_dict = {}
            for university in university_queryset:
                # Access and process each university object
                university_count_dict[university] = university.users_count()
            
            max_users_uni = max(university_count_dict, key=university_count_dict.get)
            university = max_users_uni
        else:
            university = None

    except UniversityProfile.DoesNotExist:
        university = None
    return university
