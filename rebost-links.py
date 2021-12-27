#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


import xml.etree.ElementTree as ET
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

def check_link(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        x =  urlopen(req, timeout=60)
        return 200
    except HTTPError as e:
        logging.error(f"{url} - {e}")
        return e.code
    
    except Exception as e:
        logging.error(f"{url} - {e}")
        return 523

def get_value(item, key):
    url = None
    link = False
    for child_item in item:
        #print(child_item.tag)
        if child_item.tag == '{http://wordpress.org/export/1.2/}meta_key':
            #print(child_item.text)
            if key == child_item.text:
                link = True

        if link and child_item.tag == '{http://wordpress.org/export/1.2/}meta_value':
            #print(child_item.text)
            link = False
            url = child_item.text

    return url


def get_content_urls(html):
    urls = []
    soup = BeautifulSoup(html, "html5lib")
    for a in soup.findAll('a'):
        url = a.get('href')
        if url is not None and url[0:4] == "http":
            urls.append(url)

    return urls

def print_error(json_item, url, url_type, result):

    http = "http://"
    if url[0:len(http)] == "http://":
        https_url = "https://" + url[len(http):]
        https_result = check_link(https_url)
        if https_result == 200:
            print(f"Programa {json_item['title']} - '{url_type}' {url}, error {result} - (possible nova URL {https_url} que no dóna error)")
            return

    print(f"Programa {json_item['title']} - '{url_type}' {url}, error {result} ")


def check_links(source_filename):
    tree = ET.parse(source_filename)
    root = tree.getroot()

    items = 0
    analyzed_items = 0
    broken_links = 0
    for entry in root.iter('item'):
        #print(f"tag: {entry.tag}")
        json_item = {}
        publish = False
        url = None 
        program_url = None
        download_urls = []
        content_urls = []
        status = ""

        for item in entry:
        
            if item.tag == "{http://wordpress.org/export/1.2/}status":
                if item.text == "publish":
                    publish = True

                status = item.text

            if item.tag == "title":
                json_item['title'] = item.text

     
            if item.tag == "{http://wordpress.org/export/1.2/}postmeta":
                url = get_value(item, 'lloc_web_programa')
                for i in range(0, 8):
                    download_url = get_value(item, f'baixada_{i}_download_url')
                    if download_url:
                        download_urls.append(download_url)

            if item.tag == "{http://purl.org/rss/1.0/modules/content/}encoded" and item.text is not None:
                content_urls = get_content_urls(item.text)


        if publish == False:
            continue

        if 'title' not in json_item:
            continue

        if url is not None:
            result = check_link(url)
            logging.debug(f"Checked program {url} status code: {result}")
            if result != 200:
                broken_links += 1
                print_error(json_item, url, 'lloc_web_programa', result)
            
        if len(download_urls) > 0:
            for url in download_urls:
                result = check_link(url)
                logging.debug(f"Checked download {url} status code: {result}")
                if result != 200:
                    broken_links += 1
                    print_error(json_item, url, 'download_url', result)

        if len(content_urls) > 0:
            for url in content_urls:
                result = check_link(url)
                logging.debug(f"Checked content {url} status code: {result}")
                if result != 200:
                    broken_links += 1
                    print_error(json_item, url, 'content_urls', result)

        analyzed_items += 1
        
    print(f"Analyzed {analyzed_items} items, broken links {broken_links}")


def main():
    print("Checks the links of the Softcatalà program directory (Rebost)")
    logging.basicConfig(filename="rebost-links.log", level=logging.DEBUG, filemode="w")
    check_links("raw/programes.xml")

if __name__ == "__main__":
    main()