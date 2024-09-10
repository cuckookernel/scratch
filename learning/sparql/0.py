# %%
from importlib import reload
import SPARQLWrapper as spql
from SPARQLWrapper import SPARQLWrapper, JSON

import learning.sparql.lib as lib
# %%


sparql = SPARQLWrapper(
    # "http://vocabs.ardc.edu.au/repository/api/sparql/"
    # "csiro_international-chronostratigraphic-chart_geologic-time-scale-2020"
    # "http://etytree-virtuoso.wmflabs.org/sparql" TIMEOUT
    # "https://api.triplydb.com/datasets/princeton/wordnet/services/wordnet/sparql"

)

sparql.setReturnFormat(JSON)

# %%

sparql.setQuery("""
    PREFIX gts: <http://resource.geosciml.org/ontology/timescale/gts#>

    SELECT *
    WHERE {
        ?a a gts:Age .
    }
    ORDER BY ?a
    LIMIT 100

""")
# %%
sparql.setQuery("""
 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
 SELECT ?a 
 FROM <http://www.w3.org/2000/01/rdf-schema#>
 WHERE {
    ?a a rdfs:Class .
 }
LIMIT 100
""")


# %%
sparql.setQuery("""
  PREFIX lvont: <http://lexvo.org/ontology#>
  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
  PREFIX dcterms: <http://purl.org/dc/terms/>

 SELECT ?lang ?word ?etymology WHERE {
   ?term lvont:etymology ?etymology .
   ?term rdfs:label ?word .
   ?term dcterms:language ?lang .
  FILTER regex(?word, "coffee", "i") .
}
""")
# %%
sparql.setQuery("""
 SELECT ?a ?rel ?b WHERE {
   ?a ?rel ?b .
}
LIMIT 100
""")
# %%
sparql.setQuery("""
    PREFIX ol: <http://www.w3.org/ns/lemon/ontolex#>
    PREFIX rdf: <http://www.w3.org/2000/01/rdf#>

    SELECT ?b  WHERE {
       ?a a ?b .
       
       FILTER (?b != ol:LexicalSense)
    }
    LIMIT 100
""")

# %%
sparql.setQuery("""
    PREFIX ol: <http://www.w3.org/ns/lemon/ontolex#>
    PREFIX rdf: <http://www.w3.org/2000/01/rdf#>

    SELECT DISTINCT  ?b  
    WHERE {
       ?a ?rel ?b .       
    }
""")

# resp = sparql.query()

resp = sparql.queryAndConvert()

bindings = resp['results']['bindings']
# %%

prefixes = {
  "ol": "http://www.w3.org/ns/lemon/ontolex#",
  "owl": "http://www.w3.org/2002/07/owl#",
  "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
  "dc": "http://purl.org/dc/terms/",
  "pwnl": "http://wordnet-rdf.princeton.edu/rdf/lemma/",
  "pwnol": "http://wordnet-rdf.princeton.edu/ontology#",

}

reload(lib)

mspql = lib.MySparQL(prefixes=prefixes,
                     endpoint="http://api.talis.com/stores/wordnet/services/sparql",
                     # endpoint="https://api.triplydb.com/datasets/princeton/wordnet/"
                     #         "services/wordnet/sparql"
                     )
# %%
mspql.distinct_classes()
# %%
rels = mspql.distinct_props()
# %%
df_sample = mspql.sample(offset=100)

# %%
mspql.query(
    """
     select a? ?rel b?
     WHERE {
        ?a = <pwnl:Dama#Dama-02435836-n>     
     }
    """
)
# %%
