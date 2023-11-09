# email1 = "samurai@ninja.edu"
# email2 = "samurai@ninja.edu.in"
# email3 = "samurai@ninja.ac.in"
# college_email = email3.split('.')[-1:]
# print(college_email)
# if not (college_email == ['edu']):
#     college_email = email3.split('.')[-2:]
#     print(college_email)
#     if not (college_email == ['edu', 'in'] or college_email == ['ac', 'in']):
#         print("not allowed")
from mystranger_app.utils import haversine_distance, calculate_distance

lat1 = 28.3671232
lon1 = 77.54045993787369

lat2 = '30.353478703235428'
lon2 = '76.36329004517'



distance =  haversine_distance(lat1, lon1, lat2, lon2)
# distance =  calculate_distance(lat1, lon1, lat2, lon2)
print(f"The distance between the two locations is {distance:.2f} kilometers.")