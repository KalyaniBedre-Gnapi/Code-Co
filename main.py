import googlemaps
from polyline import decode
from geopy.distance import geodesic
import requests
import os

# Replace 'YOUR_API_KEY' with your actual Google Street View Static API key
API_KEY = os.getenv("GOOGLE_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/streetview"

def download_street_view_image(location, size="640x640", heading=0, fov=90, pitch=0, save_path="street_view_image.jpg"):
    """
    Downloads a Google Street View image.

    Args:
        location (str): The address or latitude/longitude coordinates (e.g., "400 Broad St, Seattle, WA 98109" or "47.6062,-122.3321").
        size (str): The output size of the image in pixels (e.g., "640x640").
        heading (int): The compass heading of the camera (0-360 degrees, where 0 is North).
        fov (int): The horizontal field of view of the image (0-120 degrees).
        pitch (int): The up or down angle of the camera relative to the Street View vehicle (typically 0).
        save_path (str): The path where the downloaded image will be saved.
    """
    params = {
        'key': API_KEY,
        'location': location,
        'size': size,
        'heading': heading,
        'fov': fov,
        'pitch': pitch
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        if response.content:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Street View image downloaded successfully to: {save_path}")
        else:
            print("No image content received from the API.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading Street View image: {e}")

def get_points_along_street(api_key, origin, destination, interval_meters):
    """
    Generates latitude and longitude coordinates along a street at a specified interval.

    Args:
        api_key (str): Your Google Maps API key.
        origin (str): The starting address or coordinates.
        destination (str): The ending address or coordinates.
        interval_meters (int): The desired interval in meters between points.

    Returns:
        list: A list of (latitude, longitude) tuples representing points along the street.
    """
    
    api_key = 'AIzaSyD6UcaNsYMwrZnY_fwdu2svtPID1I4AsJ0'
    gmaps = googlemaps.Client(key=api_key)

    # Request directions
    directions_result = gmaps.directions(origin, destination, mode="driving")

    if not directions_result:
        print("Error: Could not get directions.")
        return []

    # Extract the encoded polyline from the first leg of the first route
    encoded_polyline = directions_result[0]['overview_polyline']['points']

    # Decode the polyline to a list of (latitude, longitude) tuples
    decoded_path = decode(encoded_polyline)

    if not decoded_path:
        print("Error: Could not decode polyline.")
        return []

    points_on_street = []
    current_distance = 0.0
    last_point = decoded_path[0]
    points_on_street.append(last_point)

    for i in range(1, len(decoded_path)):
        next_point = decoded_path[i]
        segment_distance = geodesic(last_point, next_point).meters

        while current_distance + segment_distance >= interval_meters:
            remaining_distance_to_interval = interval_meters - current_distance
            fraction = remaining_distance_to_interval / segment_distance

            # Interpolate the point
            lat = last_point[0] + fraction * (next_point[0] - last_point[0])
            lng = last_point[1] + fraction * (next_point[1] - last_point[1])
            points_on_street.append((lat, lng))

            current_distance = 0.0 # Reset for the new interval
            # Adjust the segment_distance for the remaining portion
            segment_distance -= remaining_distance_to_interval
            last_point = (lat, lng) # Update last_point for subsequent calculations
        
        current_distance += segment_distance
        last_point = next_point

    return points_on_street

# Example Usage:
if __name__ == "__main__":
    YOUR_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key
    street_name = "SE_Belmont_St" 
    start_address = "45.516442365085254, -122.62602731249221"  #3646 SE Belmont St #4326, Portland, OR 97214, United States
    end_address =  "45.51716000383131, -122.59243256233222" #6839 SE Belmont St, Portland, OR 97215, United States

#v1 ANALYSED IMAGES- #4252 NE Glisan St, Portland, OR 97213, United States to  #"6108 NE Glisan St, Portland, OR 97213, United States"
#v2 ANALYSED IMAGES-#1708 E Burnside St, Portland, OR 97214, United States to  #"18428-18440 E Burnside St Portland, OR 97233, USA
#v3 ANALYSED IMAGES   -#642 SE Stark St, Portland, OR 97214, United States to #Multnomah Friends Meeting, 4312 SE Stark St, Portland, OR 97215, United States
    interval = 15  # meters
    cnt=0
    
    latlng = ""
    
    street_points = get_points_along_street(YOUR_API_KEY, start_address, end_address, interval)
    #with open('C:\work\GNAPI_BRG\Gladvelly_Drive.txt', 'w') as file:  
    if street_points:
        for lat, lng in street_points:
            cnt = cnt + 1
            # Download an image by latitude/longitude
            save_file_path = "D:\\Code&Co\\streetview_images_v3\\" + street_name + str(cnt) + ".jpg"
            latlng = str(lat) + "," + str(lng)
            download_street_view_image(location=latlng, heading=180, size="800x800", fov=100, save_path=save_file_path)
            #print(f"Latitude: {lat}, Longitude: {lng}")
            #file.write(str(lat) + "," + str(lng)+'\n')
    
    #file.close()
    