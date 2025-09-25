from celery import shared_task
from .models import Frame, OutputImage
from PIL import Image
import os
import requests
from io import BytesIO
from django.conf import settings
import time
import logging

# Logger setup
logger = logging.getLogger(__name__)

def overlay_images(frame_path, product_image_url, coordinates):
    try:
        # Load frame image
        frame = Image.open(frame_path).convert("RGBA")
        
        # Download product image
        response = requests.get(product_image_url)
        response.raise_for_status()
        
        product_image = Image.open(BytesIO(response.content)).convert("RGBA")
        
        # Get coordinates
        x = int(coordinates.get('x', 0))
        y = int(coordinates.get('y', 0))
        width = int(coordinates.get('width', 100))
        height = int(coordinates.get('height', 100))
        
        # Resize and paste using PIL coordinate system
        resized_product = product_image.resize((width, height), Image.ANTIALIAS)
        
        # Boundary check - ensure it stays within frame bounds
        final_x = max(0, min(x, frame.size[0] - width))
        final_y = max(0, min(y, frame.size[1] - height))
        
        # Log if coordinates were adjusted
        if final_x != x or final_y != y:
            logger.warning(f"Coordinates adjusted from ({x}, {y}) to ({final_x}, {final_y}) to fit frame bounds")
        
        # PIL paste operation
        frame.paste(resized_product, (final_x, final_y), resized_product)
        
        return frame
        
    except Exception as e:
        logger.error(f"Error in overlay_images: {e}")
        raise

@shared_task
def process_feed_entries(frame_id):
    logger.info(f"Starting process_feed_entries for frame {frame_id}")
    
    try:
        frame = Frame.objects.get(id=frame_id)
        
        # Check coordinates
        if not frame.coordinates:
            logger.error(f"No coordinates set for frame {frame_id}")
            return
            
        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs', str(frame_id))
        os.makedirs(output_dir, exist_ok=True)

        feed_url = frame.xmlFeedPath
        logger.info(f"Processing feed: {feed_url}")
        
        response = requests.get(feed_url)
        response.raise_for_status()

        from xml.etree import ElementTree
        tree = ElementTree.fromstring(response.content)

        # Define namespace for Atom feed
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}

        # Get all entries
        entries = tree.findall('atom:entry', namespace)
        total_products = len(entries)
        logger.info(f"Found {total_products} products in feed")

        processed_count = 0

        for i, entry in enumerate(entries):
            product_id_elem = entry.find('atom:id', namespace)
            image_link_elem = entry.find('atom:image_link', namespace)
            
            if product_id_elem is None or image_link_elem is None:
                continue
                
            product_id = product_id_elem.text
            image_link = image_link_elem.text
            
            try:
                output_image = overlay_images(frame.image.path, image_link, frame.coordinates)
                output_path = os.path.join(output_dir, f"{product_id}.png")
                output_image.save(output_path)
                
                # Save with relative path for Django
                relative_path = f"outputs/{frame_id}/{product_id}.png"
                OutputImage.objects.create(
                    frame=frame, 
                    product_id=product_id,
                    product_image_url=image_link,
                    image=relative_path,
                )
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing product {product_id}: {e}")
                # Save failed processing record
                OutputImage.objects.create(
                    frame=frame,
                    product_id=product_id,
                    product_image_url=image_link,
                )
        
        logger.info(f"Processing completed. {processed_count}/{total_products} products processed successfully.")
        
    except Exception as e:
        logger.error(f"Fatal error processing frame {frame_id}: {e}")

@shared_task
def generate_images(frame_id):
    """This function is now replaced by process_feed_entries"""
    return process_feed_entries(frame_id)