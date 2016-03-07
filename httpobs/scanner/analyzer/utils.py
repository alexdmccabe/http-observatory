import requests
import sys

from base64 import b64decode
from json import loads


HSTS_URL = ('https://chromium.googlesource.com/chromium'
            '/src/net/+/master/http/transport_security_state_static.json?format=TEXT')
hsts = {}

# Download the Google HSTS Preload List
try:
    print('Retrieving the Google HSTS Preload list', file=sys.stderr)
    r = b64decode(requests.get(HSTS_URL).text).decode('utf-8').split('\n')

    # Remove all the comments
    r = ''.join([line.split('// ')[0] for line in r if line.strip() != '//'])

    r = loads(r)

    # Mapping of site -> whether it includes subdomains
    hsts = {site['name']: {
        'includeSubDomains': site.get('include_subdomains', False),
        'pinned': True if 'pins' in site else False,
    } for site in r['entries']}

except:
    print('Unable to download the Google HSTS Preload list; exiting', file=sys.stderr)
    exit(1)


def is_hsts_preloaded(hostname):
    # Just return true if the hostname is the HSTS list -- no need to see if includeSubDomains is set or not
    if hostname in hsts:
        return hsts[hostname]

    # Either the hostname is in the list *or* the TLD is and includeSubDomains is true
    host = hostname.split('.')
    levels = len(host)

    # If hostname is foo.bar.baz.mozilla.org, check bar.baz.mozilla.org, baz.mozilla.org, mozilla.org, and .org
    for i in range(1, levels):
        domain = '.'.join(host[i:levels])
        if domain in hsts:
            return hsts[domain]

    return False


# Return the new result if it's worse than the existing result, otherwise just the current result
def only_if_worse(new_result: str, old_result: str, order = None) -> str:
    if order is None:
        order = []

    if not old_result:
        return new_result
    elif order.index(new_result) > order.index(old_result):
        return new_result
    else:
        return old_result


# Let this file be run directly so you can see the JSON for the Google HSTS thingie
if __name__ == '__main__':
    print(hsts)