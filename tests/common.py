from rdfsync.wb2rdf.conversion import Converter

converter = Converter(endpoint='', input_format='ttl')

MEDIAWIKI_API_URL = "https://rdfsync-test.wiki.opencura.com/w/api.php"


def load_graph_from(source):
    return converter.read_file_and_create_graph('tests/data/synchronization/' + source)
