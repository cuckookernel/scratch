
from dataclasses import dataclass
from pandas import DataFrame
from SPARQLWrapper import SPARQLWrapper, JSON
from typing import Dict, Any, Union
from typing_extensions import Self
# %%


def _interactive_testing(sparql: SPARQLWrapper):
# %%
    classes = distinct_classes(sparql)

# %%


class MySparQL:
    def __init__(self, prefixes: Dict[str, str], **kwargs):
        self.prefixes = prefixes
        self.sparql: SPARQLWrapper = SPARQLWrapper(**kwargs)
        self.sparql.setReturnFormat(JSON)

    def query(self, query: str) -> DataFrame:
        prefixes_str = "\n".join(f"PREFIX {pref}: <{prefix_value}>"
                                 for pref, prefix_value in self.prefixes.items())

        self.sparql.setQuery(prefixes_str + "\n" + query)
        resp = self.sparql.queryAndConvert()

        return resp_to_df(resp, prefixes=self.prefixes)

    def distinct_classes(self) -> DataFrame:

        query = """SELECT ?class (count(?class) as ?resource_count)  
            WHERE {
               ?a a ?class .       
            }
            group by ?class
            """

        return self.query(query)

    def distinct_props(self) -> DataFrame:

        query = """SELECT ?prop (count(?prop) as ?tuple_count)  
            WHERE {
               ?a ?prop ?b .       
            }
            group by ?prop
        """

        return self.query(query)

    def sample(self, limit: int = 100, offset: int = 0) -> DataFrame:

        query = f"""SELECT ?a ?rel ?b 
            WHERE {{
                ?a ?rel ?b.                       
            }}
            LIMIT {limit}
            OFFSET {offset}
            """

        return self.query(query)


@dataclass
class URI:
    value: str

    def __str__(self):
        return self.value

    def __lt__(self, other: Self):
        return self.value < other.value


def resp_to_df(resp: Dict[str, Any], prefixes: Dict[str, str]) -> DataFrame:
    head = resp['head']
    if 'link' in head and not head['link'] and len(head['link']) > 0:
        print('Link found, but ignoring it:', head['link'] )

    columns = resp['head']['vars']
    results = resp['results']['bindings']

    data = []
    for result in results:
        # print(result)
        data_item = { k: preproc_cell(cell, prefixes) for k, cell in result.items() }
        data.append(data_item)

    return DataFrame(data, columns=columns)


def preproc_cell(cell: dict, prefixes: Dict[str, str]) -> Union[dict, URI, int]:
    if cell['type'] == 'uri':
        value = cell['value']
        return URI(value=shorten_uri(value, prefixes))
    elif cell['type'] == 'literal':
        if cell['datatype'] == 'http://www.w3.org/2001/XMLSchema#integer':
            return int(cell['value'])
        else:
            return cell
    else:
        return cell


def shorten_uri(uri_value: str, prefixes: Dict[str, str]) -> str:
    for pref, prefix_value in prefixes.items():
        if uri_value.startswith(prefix_value):
            return uri_value.replace(prefix_value, f"{pref}:")

    return uri_value
