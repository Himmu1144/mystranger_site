import math , random 
import requests

def generateOTP() :
 
    # Declare a digits variable 
    # which stores all digits
    digits = "0123456789"
    OTP = ""
 
   # length of password can be changed
   # by changing value in range
    for i in range(8) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP

def calculate_distance(lat1, lon1, lat2, lon2):
    # OpenStreetMap API URL
    url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    # Send HTTP request to the OpenStreetMap API
    response = requests.get(url)
    data = response.json()

    # Extract the distance from the API response
    if "routes" in data and len(data["routes"]) > 0:
        distance = data["routes"][0]["distance"] / 1000  # Convert meters to kilometers
        return int(distance)

    return None

