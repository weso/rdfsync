from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff
from rdflib.namespace import NamespaceManager, RDF, Namespace, RDFS
from str_util import *

def dump_nt_sorted(g):
    for l in sorted(g.serialize(format='nt').splitlines()):
        if l: print(l.decode('utf-8'))


g1 = Graph()
g1.parse("files/ex1.ttl", format="ttl")
iso1 = to_isomorphic(g1)

g2 = Graph()
g2.parse("files/ex2.ttl", format="ttl")
iso2 = to_isomorphic(g2)

# graph diff
in_both, in_first, in_second = graph_diff(iso1, iso2)

# print("present in both")
# dump_nt_sorted(in_both)  # doctest: +SKIP

# print("missing from second that exists in first")
# dump_nt_sorted(in_first)  # doctest: +SKIP

# print("missing from first that exists in second")
# dump_nt_sorted(in_second)  # doctest: +SKIP

# updating the first file from the changed made on the second copy
# final_result = g2 - g1 # changes in g2 not seen in g1

# for subject, predicate, object in g1:
#         # g1.add((subject, predicate, object))
#         print(subject, predicate, object)
#         # subject_to_string = str(subject).rsplit("/", 1)[-1]
#         # subject_name = subject_to_string.rpartition("#")[2]
#         # print(subject_name)

# for subject, predicate, object in g1:
#     if get_triple_subject_str(subject) == "ResearchPersonnel":
#         print(get_triple_predicate_str(predicate))
#         print(get_triple_object_str(object))
# NS = Namespace("http://example.com/")
# g1.add((NS.Aaa, RDF.type, NS.Xxx))
# g1.bind("ns", NS)




