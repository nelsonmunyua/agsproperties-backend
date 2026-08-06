from models import PropertyImage
from models import db
from shared.storage.storage_service import StorageService
from shared.constants import StorageFolders



class PropertyImageService:

    @staticmethod
    def create_images(property, images):

        if not images:
            return

        for index, image in enumerate(images):

            image_url = StorageService.save(
                image,
                folder=StorageFolders.PROFILE_IMAGES
            )

            db.session.add(

                PropertyImage(

                    property_id=property.id,

                    image_url=image_url,

                    is_primary=index == 0

                )

            )