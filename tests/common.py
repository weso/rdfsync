from rdfsync.wb2rdf.conversion import Converter

converter = Converter(endpoint='', input_format='ttl')


def load_graph_from(source):
    return converter.read_file_and_create_graph('tests/data/synchronization/' + source)
