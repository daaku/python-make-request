import urllib, httplib, urlparse, cgi, logging


# RFC3986: http://tools.ietf.org/html/rfc3986
def escape(s):
    # escape '/' too
    return urllib.quote(s, safe='~')

def encode_parameters(parameters):
    """
    Encode a dict to a query string.

    >>> encode_parameters({'a': 1, 'b': 2})
    'a=1&b=2'
    >>> encode_parameters({'a': 1, 'b': ['this is', 'an array']})
    'a=1&b=this%20is&b=an%20array'
    """
    parts = []
    for key, value in parameters.iteritems():
        key = escape(str(key))

        if type(value) == list:
            for each in value:
                parts.append('%s=%s' % (key, escape(str(each))))
        else:
            parts.append('%s=%s' % (key, escape(str(value))))
    return '&'.join(parts)

def make_request(url, method='GET', parameters={}, headers={}):
    """
    The url is broken down and query parameters are extracted. These are merged
    with the optional parameters argument. Values in the parameters argument
    take precedence. This function is designed for urlencoded parameters, and
    therefore does not allow an arbitrary body.

    NOTE: simplejson is required to run the tests.

    >>> import simplejson
    >>> BASE_URL = 'http://json-service.appspot.com/echo'

    Default GET with a simple URL containing the query parameters:
    >>> response = make_request(BASE_URL + '/more/path?a=1')
    >>> response.status
    200
    >>> json = simplejson.loads(response.read())
    >>> json['method']
    u'GET'
    >>> json['path']
    u'/echo/more/path'
    >>> json['query_params']
    {u'a': u'1'}


    POST request with array value using parameters.
    >>> response = make_request(BASE_URL, method='POST', parameters={'a':1, 'b': [2,3]})
    >>> response.status
    200
    >>> json = simplejson.loads(response.read())
    >>> json['method']
    u'POST'
    >>> json['path']
    u'/echo'
    >>> json['query_params']
    {}
    >>> json['post_params']
    {u'a': u'1', u'b': [u'2', u'3']}

    """

    parts = urlparse.urlparse(url)
    if parts.scheme == 'https':
        logging.debug('Using HTTPSConnection')
        connection = httplib.HTTPSConnection(parts.netloc)
    else:
        logging.debug('Using HTTPSConnection')
        connection = httplib.HTTPConnection(parts.netloc)

    # drop the query string and use it if it exists
    url = parts.scheme + '://' + parts.netloc + parts.path
    if parts.query != '':
        qs_params = dict([(k, v[0]) for k, v in cgi.parse_qs(parts.query).iteritems()])
        qs_params.update(parameters)
        parameters = qs_params

    data = encode_parameters(parameters)
    body = None

    if data and data != '':
        if method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            body = data
        else:
            url = url + '?' + data

    logging.debug('Method: ' + str(method))
    logging.debug('Url: ' + str(url))
    logging.debug('Body: ' + str(body))
    logging.debug('Headers: ' + str(headers))

    connection.request(method, url, body, headers)
    return connection.getresponse()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
