from pyquery import PyQuery as pq
import urllib
import os
import sys
prefix = "http://www.bbc.co.uk"
import re, urlparse

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

def getURLs(url):
        url = iriToUri(url)
        d = pq(urllib.urlopen(url).read())
        links = d("#taxa a:first-child")
        owl = url[url.rfind("/")+1:]+'.rdf'
        print owl
        if (len(links) == 0):
                return
        for link in links:
                href = pq(link).attr("href")
                getURLs(prefix+href)

getURLs(sys.argv[1])

