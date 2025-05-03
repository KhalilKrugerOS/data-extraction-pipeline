from pymongo import InsertOne
from .BaseDataModel import BaseDataModel
from .db_schemes.data_chunk import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId


class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNKS_NAME.value]
    
    def create_chunk(self, chunk: DataChunk):
        result = self.collection.insert_one(chunk.model_dump())
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if record is None:
            return None
        return DataChunk(**record)
    
    async def insert_many_chunks(self, chunks: list[DataChunk], batch_size: int = 100):
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            # Create a list of InsertOne operations
            operations = [InsertOne(chunk.model_dump()) for chunk in batch]
            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count