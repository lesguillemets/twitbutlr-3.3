#!/usr/bin/env python3
# coding:utf-8

import urllib.parse as urlp
import urllib.request as urlr
import xml.etree.ElementTree as elm

def wparticle(langcode, articlename):
    
    if wp_has_article(langcode, articlename):
        wpurl = "https://{}.wikipedia.org/wiki/{}".format(
                    langcode, urlp.quote(articlename))
        return (True, wpurl)
    
    else:
        wpsearch = "https://{}.wikipedia.org/wiki/Special:search/{}".format(
            langcode, urlp.quote(articlename))
        return (False,
            '"{}" : 項目が見つかりません．検索結果はこちらです {}'.format(
            articlename.replace('_',' '), wpsearch))
        

def wp_has_article(langcode, articlename):
    query = "http://{}.wikipedia.org/w/api.php?action=query&titles={}&format=xml".format(
        langcode, urlp.quote(articlename))
    with urlr.urlopen(query) as q:
        page = q.read().decode("utf-8")
    root = elm.fromstring(page)
    for page in root.iter('page'):
        return not('missing' in page.attrib)
