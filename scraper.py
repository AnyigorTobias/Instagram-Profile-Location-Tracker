import requests
import pandas as pd
import json
import base64
from datetime import datetime
import spacy
from geopy.geocoders import Nominatim
import folium
from folium.plugins import AntPath
from config import settings


CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
username = 'johnobidi'

def scrape_instagram(consumer_key, consumer_secret, username, limit):
    
    CONSUMER_KEY=consumer_key
    CONSUMER_SECRET = consumer_secret
    username = username
    url = f'https://thesocialproxy.com/wp-json/tsp/instagram/v1/profiles/feed?consumer_key={CONSUMER_KEY}&consumer_secret={CONSUMER_SECRET}&username={username}'

    payload = {}
    headers = {
      'Content-Type': 'application/json',
    }

    
    # Initialize an empty list to store all results
    all_results = []

    # Pagination handling (if applicable)
    next_page = 1  # Start with the first page
    limit= limit # Limit to the number of pages to fetch, adjust as needed

    while next_page and next_page <= limit:
        # Make the request with current page
        response = requests.get(url, headers=headers, data=payload)

        # Parse JSON response
        response_json = response.json()

        # Check if results are in the 'data' key
        if 'data' in response_json and isinstance(response_json['data'], list):
            results = response_json['data']
            all_results.extend(results)  # Add the current page results to the total list

            

            # Check if there's a next page
            next_page += 1  # Increment to the next page
        else:
            # No more data or unexpected structure
            break
            
    return all_results

from datetime import datetime
# Convert Unix timestamp to readable time
def convert_timestamp(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%dT%H:%M:%S')

def extract_location(all_results, limit):
    extracted_posts = []  # List to store all extracted data
    
    for i in range(limit):
        postx = all_results[i]['items']
        for post in postx:
            taken_at = post['taken_at']
             # Convert taken_at from Unix to readable time format
            time = convert_timestamp(taken_at) if isinstance(taken_at, int) else 'Unknown Time'
            
            # Default values for caption-related fields
            caption_text = 'No caption'
           
            # Check if 'caption' exists
            caption = post.get('caption')
            if caption:
                caption_text = caption.get('text', 'No caption')  # Extracting the caption text
            
            # Default location values
            location_name = 'Unknown Location'
            latitude = 'Unknown Latitude'
            longitude = 'Unknown Longitude'
            
            # Extract location if available
            location = post.get('location')  # Use get() to avoid KeyError if 'location' doesn't exist
            if location:
                location_name = location.get('name', 'Unknown Location')
                latitude = location.get('lat', 'Unknown Latitude')
                longitude = location.get('lng', 'Unknown Longitude')
            
            # Default value for image URL
            image_url = 'No Image URL'
            
            # Extract image URL if the post is an image
            image_versions = post.get("image_versions2", {}).get("candidates", [])
            if image_versions:
                image_url = image_versions[0].get("url", "No Image URL")
            
            # Append the extracted data
            extracted_posts.append({
                'taken_at': time,
                'caption_text': caption_text,
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude,
                'image_url': image_url  # Include the image URL
            })
    
    return extracted_posts


def get_location_from_text(posts):
    #load SpaCy model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(posts)
    # Extract any location entities (GPE)
    location = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    # initialize the nominatin from geopy for getting the coordinates
    geolocator = Nominatim(user_agent="my_app")
    location_coordinate = geolocator.geocode(location)
    if location_coordinate:
        return location_coordinate.latitude, location_coordinate.longitude
    return "Unknown Latitude", "Unknown Longitude" 


# Geolocation API call
def get_geolocation_from_image(base64_image, CONSUMER_KEY, CONSUMER_SECRET):
    try:
        url = f"https://thesocialproxy.com/wp-json/tsp/geolocate/v1/image?consumer_key={CONSUMER_KEY}&consumer_secret={CONSUMER_SECRET}"
        payload = json.dumps({
              "image": base64_image
            })
        headers = {
              'Content-Type': 'application/json',
            }

        response = requests.request("POST", url, headers=headers, data=payload)
        #response.raise_for_status()
        data = response.json()
        
        geo_predictions = data['data']['geo_predictions']
        coordinates_list = [prediction['coordinates'] for prediction in geo_predictions]
        if coordinates_list:
            return coordinates_list[0]
        else:
            return ('Unknown Latitude', 'Unknown Longitude')
    except Exception as e:
        print(f"Error during geolocation API call: {e}")
        return ('Unknown Latitude', 'Unknown Longitude')
    
    
# Function to fetch image-based geolocation if location from caption fails
def fetch_geolocation_from_image(image_url, CONSUMER_KEY, CONSUMER_SECRET):
    try:
        # Step 1: Download the image
        response = requests.get(image_url)
        #response.raise_for_status()  # Check for HTTP errors
        # Step 2: Convert the image to Base64
        image_data = response.content  # Get the image data in bytes
        base64_image = base64.b64encode(image_data).decode('utf-8')  # Encode to Base64 and decode to string
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None
    
    if base64_image:
        return get_geolocation_from_image(base64_image, CONSUMER_KEY, CONSUMER_SECRET)



def extract_location_data(posts, CONSUMER_KEY, CONSUMER_SECRET):
    location_data = []

    for post in posts:
        location = post['location_name']
        caption = post['caption_text']
        image_url = post['image_url']
        latitude = post['latitude']
        longitude = post['longitude']
        time = post['taken_at']
        
        if location == "Unknown Location":
            latitude, longitude = get_location_from_text(caption)  # Assuming this function exists elsewhere
            if latitude == "Unknown Latitude" and longitude == "Unknown Longitude":
                latitude, longitude = fetch_geolocation_from_image(image_url, CONSUMER_KEY, CONSUMER_SECRET)  # Assuming this function is defined
        
        # Append only latitude, longitude, and time to the list
        location_data.append([latitude, longitude, time])
    
    return location_data

# Sample data: [latitude, longitude, timestamp]
def create_maps(locations, filename="map_file_john_obidi.html"):
    # create a dataframe from the locations input
    location_df = pd.DataFrame(locations, columns=['latitude', 'longitude', 'timestamp']).sort_values('timestamp')
    locations = location_df.to_dict(orient='records')
    locations
    # Create a map centered around the first location
    m = folium.Map(location=[locations[0]['latitude'],locations[0]['longitude']], zoom_start=13)

    # Add markers and a path to the map
   
    coordinates = [(loc['latitude'],loc['longitude']) for loc in locations]
    AntPath(locations=coordinates, dash_array=[20, 20], pulse_color='blue').add_to(m)
    # possible approach 
    start_time  = locations[0]['timestamp']
    end_time = locations[-1]['timestamp']

    for idx, loc in enumerate(locations, start=1):
        date = datetime.fromisoformat(start_time).date()
        time = datetime.fromisoformat(start_time).time()
        if idx == 1:
            text = f"Start\nDate: {date}\nTime: {time}"
            text = folium.Popup(text, show=True)
            icon = folium.Icon(color='red')
        elif idx == len(locations):
            date = datetime.fromisoformat(end_time).date()
            time = datetime.fromisoformat(end_time).time()
            text = f"End\nDate: {date}\nTime: {time}"
            text = folium.Popup(text, show=True)
            icon = folium.Icon(color='red')
        else:
            date = datetime.fromisoformat(loc['timestamp']).date()
            time = datetime.fromisoformat(loc['timestamp']).time()
            text = f"Date: {date}\nTime: {time}"
            text = folium.Popup(text)
            icon = folium.Icon(color='blue')
        folium.Marker(
            location=[loc['latitude'], loc['longitude']],
            popup=text,
            icon=icon
        ).add_to(m)

    # Save the map to an HTML file
    m.save(filename)


