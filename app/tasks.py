from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Frame, OutputImage
from PIL import Image
import os, requests, logging
from io import BytesIO
from django.conf import settings

logger = logging.getLogger(__name__)

def overlay_images(frame_path, product_image_url, coordinates):
    frame = Image.open(frame_path).convert("RGBA")
    response = requests.get(product_image_url)
    response.raise_for_status()
    product_image = Image.open(BytesIO(response.content)).convert("RGBA")

    x = int(coordinates.get('x', 0))
    y = int(coordinates.get('y', 0))
    width = int(coordinates.get('width', 100))
    height = int(coordinates.get('height', 100))

    resized_product = product_image.resize((width, height), Image.Resampling.LANCZOS)
    final_x = max(0, min(x, frame.size[0] - width))
    final_y = max(0, min(y, frame.size[1] - height))
    frame.paste(resized_product, (final_x, final_y), resized_product)
    return frame

@shared_task(bind=True)
def process_feed_entries(self, frame_id):
    logger.info(f"Starting process_feed_entries for frame {frame_id}")
    channel_layer = get_channel_layer()
    group_name = f"progress_{frame_id}"

    try:
        frame = Frame.objects.get(id=frame_id)
        if not frame.coordinates:
            logger.error(f"No coordinates set for frame {frame_id}")
            return

        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs', str(frame_id))
        os.makedirs(output_dir, exist_ok=True)

        response = requests.get(frame.xmlFeedPath)
        response.raise_for_status()

        from xml.etree import ElementTree
        tree = ElementTree.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = tree.findall('atom:entry', namespace)
        total_products = len(entries)
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
                relative_path = f"outputs/{frame_id}/{product_id}.png"
                OutputImage.objects.create(
                    frame=frame,
                    product_id=product_id,
                    product_image_url=image_link,
                    image=relative_path
                )
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing product {product_id}: {e}")
                OutputImage.objects.create(
                    frame=frame,
                    product_id=product_id,
                    product_image_url=image_link
                )

            # Send WebSocket progress update
            async_to_sync(channel_layer.group_send)(
                f"progress_{frame_id}",
                {
                    "type": "progress_update",  # Buradaki type consumer metoduna karşılık gelmeli
                    "data": {
                        "processed": processed_count,
                        "total": total_products,
                        "product_id": product_id
                    }
                }
            )

        logger.info(f"Processing completed. {processed_count}/{total_products} products processed successfully.")
    except Exception as e:
        logger.error(f"Fatal error processing frame {frame_id}: {e}")
        async_to_sync(channel_layer.group_send)(
            f"progress_{frame_id}",
            {
                "type": "progress_update",
                "data": {
                    "error": str(e)
                }
            }
        )