# Standard library imports
import os
import json
from urlparse import urlparse

# Local imports
from log import info, warning, error
import hosts

class NoHostsFoundError(Exception):
    pass

SEARCHABLE_HOST_FILE_EXT = '.host.config'

Request = hosts.Request
QueryError = hosts.QueryError

"""
Public API interface
"""
class Web2API:
    """
    Initializes the API on the specified root directory, thus loading in memory
    all the hosts.
    
    @param root_dir Directory where the hosts config files are located, 
        relative to the current running script
    """
    def __init__(self, root_dir, host_file_ext=SEARCHABLE_HOST_FILE_EXT):
        self.root_dir = os.path.abspath(root_dir)
        self.host_file_ext = host_file_ext
        self.hosts = { } 

        info('Looking for hosts in: ', self.root_dir)
        self._load_all_hosts()
        
        info('Successfully loaded: {0} with a total of {1} hosts'.format(self.root_dir, len(self.hosts)))

    """
    Queries the specified resource provided that a suitable host has been 
    found when initializing. It will then retrieve a json response ( as dict )
    as specified in the config file.

    @param request Request to be done 
    @param session Optional session to be associated with the request
    @param auth Optional authentication data to be associated with the request
    @param proxies Optional list of proxies to be used. Every host has its
        own proxy usage configuration
    """
    def query(self, request, session=None, auth=None, proxies=None):
        if not self.hosts:
            raise NoHostsFoundError('No hosts were loaded during construction')
        
        # Retrieving domain from request
        url = request.hostname
        if not request.hostname.startswith('http://'):
            url = 'http://' + request.hostname
        
        domain = urlparse(url).hostname

        if domain not in self.hosts:
            raise NoHostsFoundError('No host found matching: ' + domain)
        
        info('Found suitable host for: ' + domain)
        return self.hosts[domain].query(request)
        


    def _load_all_hosts(self):
        try:
            for filename in os.listdir(self.root_dir):    
                if filename.endswith(self.host_file_ext):
                    with open(os.path.join(self.root_dir, filename)) as fs:
                        info('Found host: ', filename)
                        try:
                            host = hosts.SearchableHost(json.loads(fs.read()))
                            if host.domain in self.hosts:
                                warning('Duplicate config file found for: ', host.domain)
                            else:
                                self.hosts[host.domain] = host
                            info('Successfully loaded config file for: ', host.domain)
                        except hosts.InvalidConfigFileError as e:
                            error('Failed to load: ', filename, ' with error: ', str(e))
                        except ValueError as e:
                            error('Failed to load: ', filename, ' invalid json error: ', str(e))
        except OSError as e:
            error('Failed to find root directory with error: ', str(e))
