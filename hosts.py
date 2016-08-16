"""
Sample configuration file for hosts. NOTE This can be tweaked manually, but 
generation should be left to the javascript frontend

Valid Root Elements. They will be enclosed in square brackets if optional
base_url : www.google.com | Base URL for the API, this is unique and there can 
    only be one configuration file for each domain

[cache_limit] : 512 | Limit in MB that the cache is allowed to use 
[cache_timeout] : 2.0 | Time in seconds after which the cache entry is removed

display_pages : [] | List of DisplayPage
item_pages : [] | List of item pages 

"""

# Standard library imports
from urlparse import urlparse
import re

# Local imports 
from log import info, warning


HOST_CONFIG_DEFAULT_CACHE_LIMIT = 0
HOST_CONFIG_DEFAULT_CACHE_TIMEOUT = 0.0

HOST_CONFIG_BASE_URL = 'base_url'
HOST_CONFIG_CACHE_LIMIT = 'cache_limit'
HOST_CONFIG_CACHE_TIMEOUT = 'cache_timeout'
HOST_CONFIG_DISPLAY_PAGES = 'display_pages'
HOST_CONFIG_ITEM_PAGES = 'item_pages'
HOST_CONFIG_RATING = 'rating'

HOST_CONFIG_DP_ID = 'id'
HOST_CONFIG_DP_ACTION = 'action'
HOST_CONFIG_DP_METHOD = 'method'
HOST_CONFIG_DP_ARGS = 'args'
HOST_CONFIG_DP_NEXT = 'next_uri'
HOST_CONFIG_DP_ITEM = 'item_uri'
HOST_CONFIG_DP_ITEM_ID = 'item_id'

HOST_CONFIG_IP_ID = 'id'
HOST_CONFIG_IP_ELEMENTS = 'elements'


class InvalidConfigFileError(Exception):
    pass

class RequiredElementNotFoundError(Exception):
    pass

class InvalidElementURIFormat(Exception):
    pass

class QueryError(Exception):
    pass

def _load_value(data, attrname, optional=False, default=None):
    if attrname in data:
        return data[attrname]
    
    if optional:
        return default
    
    raise RequiredElementNotFoundError('Failed to find element: ' + attrname)

class Tag:
    def __init__(self, tag, id_val, class_val):
        self.tag = tag
        self.id_val = id_val
        self.class_val = class_val

    def __str__(self):
        return "Node({0},{1},{2})".format(self.tag, self.id_val, self.class_val)

"""
Structure of uris is as follows:
<target>[<tag>id,class]*
target is what we are looking for, can be an attribute or a special keyword
tag is the HTML tag for that level
id,class = id and class for the preceding tag
"""
class ElementURI:
    TARGET_RE_GROUP = 'target'
    TARGET_RE = r'(?P<{0}><[a-zA-Z0-9]*>)'.format(TARGET_RE_GROUP)

    TAG_RE_GROUP = 'tags'
    ID_RE_GROUP = 'id'
    CLASS_RE_GROUP = 'class'
    TAGS_RE = r'<(?P<{0}>[a-zA-Z]*)>(?P<{1}>[a-zA-Z0-9\s_-]*),(?P<{2}>[a-zA-Z0-9\s_-]*)'.format(TAG_RE_GROUP, ID_RE_GROUP, CLASS_RE_GROUP)

    def __init__(self, string):
        self.target = None
        self.tags = []

        target_re = re.compile(ElementURI.TARGET_RE)
        match = target_re.match(string)
        if not match:
            raise InvalidElementURIFormat('Invalid URI format: ' + string)
        
        # Removing angular brackets
        self.target = match.group(ElementURI.TARGET_RE_GROUP)[1:-1]

        # Moving to tags
        string = string[match.end():]
        tags_re = re.compile(ElementURI.TAGS_RE)
        while match:
            match = tags_re.match(string)
            if match:
                self.tags.append(match.group(ElementURI.TAG_RE_GROUP), match.group(ElementURI.ID_RE_GROUP), match.group(ElementURI.CLASS_RE_GROUP))
                string = string[match.end():]


class DisplayPage:
    def __init__(self, data):
        self.id = None
        self.action = None
        self.method = None
        self.args = None
        self.item_uri = None
        self.next_uri = None
        self.item_id = None

        try:
            self.id = _load_value(data, HOST_CONFIG_DP_ID)
            self.action = _load_value(data, HOST_CONFIG_DP_ACTION)
            self.method = _load_value(data, HOST_CONFIG_DP_METHOD)
            self.args = _load_value(data, HOST_CONFIG_DP_ARGS)
            self.item_uri = ElementURI(_load_value(data, HOST_CONFIG_DP_ITEM))
            self.next_uri = ElementURI(_load_value(data, HOST_CONFIG_DP_NEXT))
            self.item_id = _load_value(data, HOST_CONFIG_DP_ITEM_ID)
        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))

class ItemPage:
    def __init__(self, data):
        self.id = None
        self.items = { }

        try:
            self.id = _load_value(data, HOST_CONFIG_IP_ID)
            
            for key,value in _load_value(data, HOST_CONFIG_IP_ELEMENTS).iteritems():
                self.items[key] = ElementURI(value)

        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))

class Rating:
    def __init__(self):
        pass

class Request:
    def __init__(self):
        self.hostname = ''
        self.id = ''

class SearchableHost:
    def __init__(self, data):
        self.domain = ''
        self.base_url = ''
        self.cache_limit = 0
        self.cache_timeout = 0.0

        self.display_pages = { } 
        self.item_pages = { }

        self._init_from_data(data)

    def _init_from_data(self, data):
        try:
            self.base_url = _load_value(data, HOST_CONFIG_BASE_URL)
            self.cache_limit = _load_value(data, HOST_CONFIG_CACHE_LIMIT, True, HOST_CONFIG_DEFAULT_CACHE_LIMIT)
            self.cache_timeout = _load_value(data, HOST_CONFIG_CACHE_TIMEOUT, True, HOST_CONFIG_CACHE_TIMEOUT)

            for page in _load_value(data, HOST_CONFIG_DISPLAY_PAGES):
                dp = DisplayPage(page)
                if dp.id in self.display_pages:
                    warning('Found duplicate for display page with id: ', dp.id)
                else:
                    self.display_pages[dp.id] = dp

            for page in _load_value(data, HOST_CONFIG_ITEM_PAGES):
                ip = ItemPage(page)
                if ip.id in self.item_pages:
                    warning('Found duplicate for item page with id: ', ip.id)
                else:
                    self.item_pages[ip.id] = ip
            
            if not self.base_url.startswith('http://'):
                self.base_url = 'http://' + self.base_url
            self.domain = urlparse(self.base_url).hostname

        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))
    
    def query(self, request):
        # Let's see what kind of request the user wants:
        if request.id in self.item_pages:
            info('Found valid ID for single page: ', str(request.id))

            return
        
        if request.id in self.display_pages:
            info('Found valid ID for display page: ', str(request.id))

            return

        raise QueryError('ID: ' + str(request.id) + ' not found for host: ' + self.domain)
            