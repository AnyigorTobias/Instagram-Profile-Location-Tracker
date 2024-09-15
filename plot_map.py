from scraper import (
    scrape_instagram, extract_location, convert_timestamp,
    extract_location_data, fetch_geolocation_from_image,
    get_location_from_text, get_geolocation_from_image,
    create_maps
)
from config import settings

def main():
    # Define your parameters
    username = 'johnobidi'
    CONSUMER_KEY = settings.CONSUMER_KEY
    CONSUMER_SECRET = settings.CONSUMER_SECRET
    limit = 10

    # Scrape the data from the Instagram profile and store in the variable data
    data = scrape_instagram(CONSUMER_KEY, CONSUMER_SECRET, username, limit)
    
    # Get the necessary information using the extract_location function
    posts = extract_location(data, len(data))
    
    # Extract location data
    location_data = extract_location_data(posts, CONSUMER_KEY, CONSUMER_SECRET)
    
    # Create maps from location data
    create_maps(location_data)

if __name__ == "__main__":
    main()
