###############################
#   Author: Prajjwal Kandel   #
#   Date created: 07/20/2018  #
###############################
import json
import requests

SUB_CLASS_URI = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
SPARQL_URL = "http://dbpedia.org/sparql"


def query(q, epr, f='application/json'):
    try:
        params = {'query': q}
        resp = requests.get(epr, params=params, headers={'Accept': f})
        return resp.text
    except Exception as e:
        print(e)
        raise


def generate_ontology(identifier, identifier_class):
    identifier_url = get_identifier_url(identifier, identifier_class)
    print(identifier_url)
    if identifier_url is not None:
        result = query(construct_query(identifier_url), SPARQL_URL)
        subclasses = get_subclasses_from_json(result)
        hierarchy = form_hierarchy(identifier_class, subclasses)
        hierarchy.append(identifier)
        return hierarchy
    else:
        return [identifier]


def main():
    identifier = "Lebron James"
    identifier_class = "Agent"
    print(generate_ontology(identifier, identifier_class))


def construct_query(identifier_url):
    return "CONSTRUCT WHERE {<" + identifier_url + "> a ?c1 ; a ?c2 . ?c1 rdfs:subClassOf ?c2 . ?c1 " \
                                                   "rdfs:label ?label . FILTER (LANG(?label)='en')}"


def get_subclasses_from_json(query_result):
    obj = json.loads(query_result)
    subclasses = {}
    for key in obj.keys():
        if key.startswith('http://dbpedia.org/ontology'):
            subclass = get_subclass(key)
            if subclass in ["Agent", "Place"]:
                continue
            else:
                for ontology in obj[key][SUB_CLASS_URI]:
                    if ontology["value"].startswith('http://dbpedia.org/ontology'):
                        subclasses[get_subclass(ontology["value"])] = subclass
                        break;
    print(subclasses)
    return subclasses


def form_hierarchy(identifier_class, subclasses):
    hierarchy = []
    current_key = identifier_class
    for i in range(0, len(subclasses)):
        if current_key not in subclasses:
            break
        hierarchy.append(subclasses[current_key])
        current_key = subclasses[current_key]
    return hierarchy


def get_subclass(url):
    return url.split('/')[-1]


def format_identifier(identifier):
    words = identifier.title().split(' ')
    if len(words) == 1:
        return words[0]
    else:
        return "_".join(words)


def get_identifier_url(identifier, identifier_class):
    request_url = "http://lookup.dbpedia.org/api/search/KeywordSearch?QueryClass={}&QueryString={}".format(
        identifier_class, identifier)
    results = requests.get(request_url, headers={'Accept': 'application/json'}).json()['results']
    if results:
        return results[0]['uri']


if __name__ == "__main__":
    main()
