
import json
from typing import Any, Dict

import bs4
import requests
from bs4 import Tag

SOURCE_URL = ("https://raw.githubusercontent.com/datamade/probablepeople/master/"
              "name_data/labeled/person_labeled.xml")
# %%


def convert():
    # %%
    # assert tag abbreviations are unique
    assert len(SHORT_TAG) == len(set(SHORT_TAG.values()))
    response = requests.get(SOURCE_URL)
    soup = bs4.BeautifulSoup(response.text, features='xml')
    full_names = list(soup.find_all('Name'))

    with open("person_labeled.json", "w") as f_out:
        for full_name in full_names:
            dic = process_full_name(full_name)
            # print(full_name)
            print(json.dumps(dic), file=f_out)
    # %%


SHORT_TAG = {
    "FirstInitial": "FI",
    "PrefixMarital": "PM",
    "PrefixOther": "PO",
    "GivenName": "GN",
    "Nickname": "NN",
    "Surname": "SN",
    "MiddleInitial": "MI",
    "LastInitial": "LI",
    "MiddleName": "MN",
    "And": "&",
    "SuffixGenerational": "SG",
    "SuffixOther": "SO",
}


def process_full_name(full_name: Tag) -> Dict[str, Any]:
    """Extract a dict with an array of tokens and a parallel array of
    tags from an xml expressed name.

    Example:
    -------
        full_name=<Name><GivenName>Jianxiong</GivenName> <Surname>Xiao</Surname></Name>
        =>
            {'tokens': ['Jianxiong', 'Xiao'], 'tags': ['GN', 'SN']}
    """
    elems = list(full_name.children)
    tokens = []
    tags = []
    for elem in elems:
        if isinstance(elem, Tag):
            try:
                tokens.append(elem.text)
                tags.append(SHORT_TAG[elem.name])
            except AttributeError:
                print(repr(elem), type(elem))

    return dict(tokens=tokens, tags=tags)
    # %%
