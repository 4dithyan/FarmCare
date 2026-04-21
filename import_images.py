import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmcare.settings')
django.setup()

from core.models import GalleryImage
from django.core.files import File

source_dir = r"d:\Theres\Adithya\FarmCare\images"
dest_dir = r"d:\Theres\Adithya\FarmCare\media\gallery"

if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Clear existing if any
GalleryImage.objects.all().delete()

titles = [
    "Harvest Fresh",
    "Cardamom Grove",
    "Processing Unit",
    "Lush Spices",
    "Premium Pods",
    "Farmer Care"
]

for idx, filename in enumerate(os.listdir(source_dir)):
    if idx >= len(titles): break
    if not os.path.isfile(os.path.join(source_dir, filename)): continue
    
    source_path = os.path.join(source_dir, filename)
    
    with open(source_path, 'rb') as f:
        img_obj = GalleryImage(
            title=titles[idx],
            category='farm'
        )
        img_obj.image.save(filename, File(f), save=True)
        print(f"Added {filename} to GalleryImage")

print("Done!")
