# Standard library imports
from urlparse import urlparse
import re
import math
import BeautifulSoup
import difflib

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
HOST_CONFIG_IP_PATHNAME = 'pathname'
HOST_CONFIG_IP_ELEMENTS = 'elements'

HC_RATING_DEPTH_TRUST_THRESHOLD = 'depth_trust_threshold'
HC_RATING_ID_TRUST_RATIO = 'id_trust_ratio'
HC_RATING_CLASS_TRUST_RATIO = 'class_trust_ratio'
HC_RATING_MITIGATION_THRESHOLD = 'mitigation_threshold'
HC_RATING_TRUST_THRESHOLD = 'trust_threshold'
HC_RATING_FULL_MATCH_ADVANTAGE = 'full_match_advantage'

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

def id_from_bs_elem(elem):
    for attr in elem.attrs:
        if attr[0] == 'id':
            return attr[1]
    return ''

def class_from_bs_elem(elem):
    for attr in elem.attrs:
        if attr[0] == 'class':
            return attr[1]
    return ''

    

"""
Structure of uris is as follows:
<target>[<tag>id,class]*
target is what we are looking for, can be an attribute or a special keyword
tag is the HTML tag for that level
id,class = id and class for the preceding tag
"""
class ElementURI:
    TARGET_RE_GROUP = 'target'
    TARGET_RE = r'(?P<{0}><[a-zA-Z]*>)\<[a-zA-Z]*\>'.format(TARGET_RE_GROUP)

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
            self.target = None
        else:
            # Removing angular brackets
            self.target = match.group(ElementURI.TARGET_RE_GROUP)[1:-1]
            string = string[match.end():]

        # Moving to tags
        tags_re = re.compile(ElementURI.TAGS_RE)
        while True:
            match = tags_re.match(string)
            if match:
                self.tags.append(Tag(match.group(ElementURI.TAG_RE_GROUP), match.group(ElementURI.ID_RE_GROUP), match.group(ElementURI.CLASS_RE_GROUP)))
                string = string[match.end():]
            else:
                break
        self.tags = self.tags[::-1]
    
    def rate(self, bs_elem, depth, rating):
        bs_id = id_from_bs_elem(bs_elem)
        bs_class = class_from_bs_elem(bs_elem)

        id_dist = difflib.SequenceMatcher(None, bs_id, self.tags[depth].id_val).ratio()
        class_dist = difflib.SequenceMatcher(None, bs_class, self.tags[depth].class_val).ratio()

        importance = rating.depth_trust_threshold / math.pow((depth + math.sqrt(rating.depth_trust_threshold)), 2)
        rampup = min((depth / rating.mitigation_threshold) * (depth / rating.mitigation_threshold), 1)
        return rampup * importance *(id_dist * rating.id_trust_ratio + class_dist * rating.class_trust_ratio)

    """
    Finds all the references matching the current ElementURI inside the html page
    based off the specified rating system
    """
    def find_all(self, html_data, rating):
        if not self.tags: # TODO:: Should I output some kind of warning ? 
            return None

        results = []

        soup = BeautifulSoup.BeautifulSoup(html_data)
        tmp_elems = soup.findAll(self.tags[-1].tag)
        elems_to_eval = []
        for element in tmp_elems:
            id_dist = difflib.SequenceMatcher(None, id_from_bs_elem(element), self.tags[-1].id_val).ratio()
            class_dist = difflib.SequenceMatcher(None, class_from_bs_elem(element), self.tags[-1].class_val).ratio()
            if id_dist > rating.generable_dist and class_dist > rating.generable_dist:
                elems_to_eval.append(element)

        final_res = []

        for result in elems_to_eval:
            total = 0.0

            res_id = id_from_bs_elem(result)
            res_class = class_from_bs_elem(result)

            # TODO: Think this through
            #if self.tags[-1].id_value == res_id and self.tags[-1].class_value == res_class:
                #total += rating.full_match_advantage

            # Calculate result depth
            next_res = result
            depth = 0
            while next_res:
                next_res = next_res.parent
                depth += 1

            expected_depth = len(self.tags)
            to_eval = result

            # Need to discard some nodes
            args_delta = 0
            if depth > expected_depth:
                delta_depth = depth - expected_depth
                while delta_depth > 1:
                    to_eval = to_eval.parent
                    delta_depth -= 1
            else:
                args_delta = expected_depth - depth +1
                # Assuming max trust on lost elements
                for i in range(expected_depth - depth, expected_depth):
                    total += rating.depth_trust_threshold / math.pow((i + math.sqrt(rating.depth_trust_threshold)), 2)

            # we climb up to delta_depth
            evaluated = 0
            while to_eval:
                total += self.rate(to_eval, expected_depth - args_delta - evaluated - 1, rating)
                evaluated += 1
                to_eval = to_eval.parent


            trust = total / rating.area_integral
            if trust >= rating.trust_threshold:
                final_res.append(result)

        return final_res


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
        self.pathname = None
        self.items = { }

        try:
            self.id = _load_value(data, HOST_CONFIG_IP_ID)
            self.pathname = _load_value(data, HOST_CONFIG_IP_PATHNAME)
            
            for key,value in _load_value(data, HOST_CONFIG_IP_ELEMENTS).iteritems():
                self.items[key] = ElementURI(value)

        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))

    def match(self, html_page, rating):
        ret = { } 

        for key,value in self.items.iteritems():
            ret[key] = value.find_all(html_page, rating)

        return ret

class Rating:
    def __init__(self, data):
        self.generable_dist = 0.7
        self.depth_trust_threshold = None
        self.id_trust_ratio = None
        self.class_trust_ratio = None
        self.mitigation_threshold = None
        self.trust_threshold = None
        self.full_match_advantage = None
        self.area_integral = None

        try:
            self.depth_trust_threshold = _load_value(data, HC_RATING_DEPTH_TRUST_THRESHOLD)
            self.id_trust_ratio = _load_value(data, HC_RATING_ID_TRUST_RATIO)
            self.class_trust_ratio = _load_value(data, HC_RATING_CLASS_TRUST_RATIO)
            self.mitigation_threshold = _load_value(data, HC_RATING_MITIGATION_THRESHOLD)
            self.trust_threshold = _load_value(data, HC_RATING_TRUST_THRESHOLD)
            self.full_match_advantage = _load_value(data, HC_RATING_FULL_MATCH_ADVANTAGE)

            assert(self.id_trust_ratio + self.class_trust_ratio <= 1.0001)

            self.area_integral = 0
            for i in range(100):
                self.area_integral += self.depth_trust_threshold / math.pow((i + math.sqrt(self.depth_trust_threshold)), 2)

        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))
    
    def __str__(self):
        return """Rating:
Generable distance: {0}
Depth trust threshold: {1}
Id trust ratio: {2}
Class trust ratio: {3}
Mitigation threshold: {4}
Trust threshold: {5}
Full match advantage: {6}
Area integral: {7}""".format(self.generable_dist, self.depth_trust_threshold, self.id_trust_ratio, self.class_trust_ratio, 
        self.mitigation_threshold, self.trust_threshold, self.full_match_advantage, self.area_integral)

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
        self.rating = None

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

            self.rating = Rating(_load_value(data, HOST_CONFIG_RATING))

        except RequiredElementNotFoundError as e:
            raise InvalidConfigFileError(str(e))
    
    def query(self, request, session):
        # Let's see what kind of request the user wants:
        if request.id in self.item_pages:
            info('Found valid ID for single page: ', str(request.id))

            html_data = session.wget(self.base_url + self.item_pages[request.id].pathname)
            result = self.item_pages[request.id].match(html_data, self.rating)

            return result
        
        if request.id in self.display_pages:
            info('Found valid ID for display page: ', str(request.id))
            return

        raise QueryError('ID: ' + str(request.id) + ' not found for host: ' + self.domain)