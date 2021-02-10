from .common import MEDIAWIKI_API_URL
from rdfsync.wb2rdf.conversion import Converter

converter = Converter(endpoint=MEDIAWIKI_API_URL, input_format='ttl', day_num=365)
items_changed_during_last_year_list \
    = {'Q5', 'Q7', 'P10', 'P8', 'Q11', 'Q2', 'P3', 'Q10', 'P7', 'Q3', 'Q4', 'Q1', 'Q6', 'Q9', 'Q8'}


def test_list_of_items_to_change():
    items_list = converter.get_items_properties_to_sync()
    assert items_list.issubset(items_changed_during_last_year_list)
