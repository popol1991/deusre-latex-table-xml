import json
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

URL = 'http://export.arxiv.org/oai2'

registry = MetadataRegistry()
registry.registerReader('oai_dc', oai_dc_reader)
client = Client(URL, registry)

for record in client.listRecords(metadataPrefix="oai_dc"):
    if record[1] is not None:
        print json.dumps(record[1].getMap())
