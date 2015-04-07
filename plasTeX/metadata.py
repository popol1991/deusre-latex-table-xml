import json
from bson.objectid import ObjectId
from pymongo import MongoClient

class Metadata():
    def __init__(self, path):
        """Init with a file containing mapping from external id to internal id
        """
        self.client = MongoClient()
        self.db = self.client.arxiv
        self.metadata = self.db.metadata
        self.external2internal_map = {}
        with open(path) as fin:
            for line in fin:
                external, internal = line.strip().split('\t')
                self.external2internal_map[external] = internal

    def get_meatadata_with_external(self, external_id):
        if external_id in self.external2internal_map:
            internal = self.external2internal_map[external_id]
            meta = self.metadata.find_one({"_id" : ObjectId(internal)})
        else:
            meta = dict(description="",title="",subject="")
        return meta

if __name__ == '__main__':
    meta = Metadata("../mapping.txt")
    jsn = meta.get_meatadata_with_external("http://arxiv.org/abs/0704.0001")
    jsn.pop("_id", None)
    print json.dumps(jsn)

