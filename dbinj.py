import json
from pymongo import MongoClient

if __name__ == '__main__':
    client = MongoClient()
    db = client.arxiv
    coll = db.metadata

    #fout = open("metaid.txt", "w")
    with open("./metadata.json") as fin:
        for line in fin:
            meta = json.loads(line)
            print meta['identifier'][0]
            #metaid = coll.insert(meta)
            #fout.write(str(metaid))
            #fout.write("\n")
    #fout.close()
