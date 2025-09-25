import requests
from xml.etree import ElementTree

def parse_feed_and_get_first_image(feed_url):
    response = requests.get(feed_url)
    response.raise_for_status()

    tree = ElementTree.fromstring(response.content)
    
    # Define namespace for Atom feed
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    first_entry = tree.find('atom:entry', namespace)
    if first_entry is not None:
        image_link = first_entry.find('atom:image_link', namespace)
        if image_link is not None:
            return image_link.text

    return None

def parse_feed_and_get_images(feed_url):
    response = requests.get(feed_url)
    response.raise_for_status()

    tree = ElementTree.fromstring(response.content)
    
    # Define namespace for Atom feed
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    image_links = []
    # Use proper namespace to find entries
    for entry in tree.findall('atom:entry', namespace):
        image_link = entry.find('atom:image_link', namespace)
        if image_link is not None:
            image_links.append(image_link.text)
    
    print(f"Found {len(image_links)} image links.")
    return image_links