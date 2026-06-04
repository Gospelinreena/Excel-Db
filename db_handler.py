from pymongo import MongoClient, errors


class MongoDBHandler:

    def __init__(self, config):

        self.config = config
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):

        try:

            self.client = MongoClient(
                self.config.MONGODB_URI
            )

            self.client.admin.command("ping")

            self.db = self.client[
                self.config.DATABASE_NAME
            ]

            self.collection = self.db[
                self.config.COLLECTION_NAME
            ]

            print("MongoDB Connected")

            return True

        except Exception as e:

            print(f"Connection Error: {e}")

            return False

    def create_schema(self, mongo_types):

        schema_properties = {}

        type_mapping = {
            "string": "string",
            "int": "int",
            "double": "double",
            "bool": "bool",
            "date": "date"
        }

        for col, dtype in mongo_types.items():

            schema_properties[col] = {
                "bsonType": type_mapping.get(
                    dtype,
                    "string"
                )
            }

        schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": schema_properties
            }
        }

        try:

            if (
                self.config.COLLECTION_NAME
                not in self.db.list_collection_names()
            ):

                self.db.create_collection(
                    self.config.COLLECTION_NAME,
                    validator=schema
                )

                print("Schema Created")

        except Exception as e:

            print(f"Schema Creation Error: {e}")

    def insert_many(self, records):

        total_inserted = 0

        for i in range(
            0,
            len(records),
            self.config.BATCH_SIZE
        ):

            batch = records[
                i:i + self.config.BATCH_SIZE
            ]

            try:

                result = self.collection.insert_many(
                    batch,
                    ordered=False
                )

                total_inserted += len(
                    result.inserted_ids
                )

            except errors.BulkWriteError as e:

                inserted = (
                    len(batch)
                    - len(e.details["writeErrors"])
                )

                total_inserted += inserted

        return total_inserted

    def create_indexes(self):

        if "date" in self.collection.index_information():
            return

        self.collection.create_index("date")
        self.collection.create_index("stock")

        self.collection.create_index(
            [
                ("stock", 1),
                ("date", -1)
            ]
        )

    def close(self):

        if self.client:
            self.client.close()