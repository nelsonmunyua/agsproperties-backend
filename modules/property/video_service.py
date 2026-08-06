from models import PropertyVideo
from models import db
from shared.storage.storage_service import StorageService
from shared.constants import StorageFolders



class PropertyVideoService:

    @staticmethod
    def create_videos(property, videos):

        if not videos:
            return

        for video in videos:

            video_url = StorageService.save(

                video,

                folder=StorageFolders.PROPERTY_VIDEOS

            )

            db.session.add(

                PropertyVideo(

                    property_id=property.id,

                    video_url=video_url

                )

            )