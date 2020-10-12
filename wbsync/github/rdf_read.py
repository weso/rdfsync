from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff

g1 = Graph()
g1.parse("examples/example-3.ttl", format="ttl")
iso1 = to_isomorphic(g1)

g2 = Graph()
g2.parse("examples/example-4.ttl", format="ttl")
iso2 = to_isomorphic(g2)

# print("are they equals ? " + iso1 == iso2)  # are not equals DUH

# graph diff
in_both, in_first, in_second = graph_diff(iso1, iso2)


def dump_nt_sorted(g):
    for l in sorted(g.serialize(format='nt').splitlines()):
        if l: print(l.decode('utf-8'))


print("present in both")
dump_nt_sorted(in_both)  # doctest: +SKIP

print("missing from second that exists in first")
dump_nt_sorted(in_first)  # doctest: +SKIP

print("missing from first that exists in second")
dump_nt_sorted(in_second)  # doctest: +SKIP

# updating the first file from the changed made on the second copy
# final_result = g1 ^ g2
# final_result.serialize(destination='examples/merged.ttl', format='turtle')
