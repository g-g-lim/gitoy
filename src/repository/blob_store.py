from database.database import Database
from database.entity.blob import Blob
from util.array import unique
from util.result import Result


class BlobStore:
    def __init__(self, database: Database):
        self.database = database

    def create(self, blobs: list[Blob]) -> Result:
        if len(blobs) == 0:
            return Result.Ok([])

        blobs = list(unique(blobs, "object_id"))
        existing_blobs = self.database.list_blobs_by_ids(
            [blob.object_id for blob in blobs]
        )
        existing_blob_ids = [blob.object_id for blob in existing_blobs]
        should_create_blobs = [
            blob for blob in blobs if blob.object_id not in existing_blob_ids
        ]
        self.database.create_blobs(should_create_blobs)
        return Result.Ok(should_create_blobs)
