from rdflib import Graph, URIRef
from rdflib.compare import to_isomorphic, graph_diff


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

for subject, predicate, object in g1:
    if not (subject, predicate, object) in g2:
        # g1.add((subject, predicate, object))
        # subject_to_string = str(subject).rsplit("/", 1)[-1]
        # subject_name = subject_to_string.rpartition("#")[2]
        # print(subject_name)
        g2.add((subject, predicate, object))

g1.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
g1.serialize(destination='files/final.ttl', format='ttl')

