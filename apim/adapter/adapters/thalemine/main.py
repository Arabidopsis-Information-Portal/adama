import json
import urlparse

import requests

URL = 'http://bar.utoronto.ca/webservices/get_expressologs.php'


def process(args):
    """Standard JSON object `args` has the form::

        {"query": <query>,
         "countOnly": False,
         "pageSize": 100,
         "page": 1}

    where `<query>` is AIP formatted query.

    """

    query = args['query']
    locus = query['locus']
    param = '[{{"gene":"{locus}"}}]'.format(locus=locus)

    # original response from 3rd party service
    native_response = requests.get(URL, params={'request': param}).json()

    hits = native_response[locus]
    for hit in hits:
        process_one(hit, locus)

    print('END')


def process_one(hit, locus):
    """Process one entry of the response."""

    # parse `efp_link` url to extract query parameters
    efp_link = hit['efp_link']
    efp_query = urlparse.urlparse(efp_link).query
    parsed_efp_query = urlparse.parse_qs(efp_query)

    # Output coexpression result
    coexpression_result = {
        'class': 'locus_relationship',
        'reference': 'TAIR10',
        'locus': locus,
        'type': 'coexpression',
        'related_entity': parsed_efp_query['primaryGene'],
        'direction': 'undirected',
        'score': [
            {'correlation_coefficient': hit['correlation_coefficient']}],
        'source': parsed_efp_query['dataSource']}
    print(json.dumps(coexpression_result, indent=4))
    print('---')

    # Output similarity result
    similarity_result = coexpression_result
    similarity_result.update(
        {'type': 'similarity',
         'score': [
             {'similarity_percentage': hit['seq_similarity']}]})
    print(json.dumps(similarity_result, indent=4))
    print('---')