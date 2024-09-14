import requests
import json
import spacy

from config import settings
username = 'oivindhaug'

CONSUMER_KEY=settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET

def scrape_instagram(CONSUMER_KEY,CONSUMER_SECRET,USERNAME, limit):
    

    #the ScrapY AI endpoints for scraping data from an instagram folder
    
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

def extract_location(all_results, limit):
    extracted_posts = []  # List to store all extracted data
    
    for i in range(limit):
        postx = all_results[i]['items']
        for post in postx:
            taken_at = post['taken_at']
            
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

                print(f"Location: {location_name} (Lat: {latitude}, Lng: {longitude})")
            else:
                print("No location data available for this post.")
                
            # Append the extracted data
            extracted_posts.append({
                'taken_at': taken_at,
                'caption_text': caption_text,
                'location_name': location_name,
                'latitude': latitude,
                'longitude': longitude
            })
    
    return extracted_posts


# Scrape the data from the instagram profile and store in the variable data
data = scrape_instagram(CONSUMER_KEY,CONSUMER_SECRET,username,10)
# Extract the locations
posts = extract_location(data,10)