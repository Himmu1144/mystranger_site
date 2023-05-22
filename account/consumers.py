from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from mystranger_app.models import University


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

        try:
            name = email.split('@')[-1:][0]
            university = await fetch_university(name)
            if university:
                lat = university.lat
                lon = university.lon
                university = university.universityName
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
                }

                try:
                    if name in universities_database:
                        info = universities_database[name]
                        university = info[0]
                        lat = info[1]
                        lon = info[2]
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)

        await self.send_json(
            {
                'universityName': str(university),
                'lat': lat,
                'lon': lon,
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
