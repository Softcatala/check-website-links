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


def check_links(source_filename):
    tree = ET.parse(source_filename)
    root = tree.getroot()

    items = []
    words = 0
    for entry in root.iter('item'):
        #print(f"tag: {entry.tag}")
        json_item = {}
        publish = False
        for item in entry:
            #print(item.tag)
        
            program_url = None
            download_urls = []
            if item.tag == "{http://wordpress.org/export/1.2/}status":
                if item.text == "publish":
                    publish = True

            if item.tag == "title":
                json_item['title'] = item.text

            if item.tag == "{http://wordpress.org/export/1.2/}postmeta":
                url = get_value(item, 'lloc_web_programa')
                for i in range(0, 8):
                    download_url = get_value(item, f'baixada_{i}_download_url')
                    if download_url:
                        download_urls.append(download_url)

            if publish and url is not None:
                result = check_link(url)
                logging.debug(f"Checked {url} status code: {result}")
                if result != 200:
                    print(f"Programa {json_item['title']} - 'lloc_web_programa' {url}, error {result} ")

            if publish and len(download_urls) > 0:
                for url in download_urls:
                    result = check_link(url)
                    logging.debug(f"Checked {url} status code: {result}")
                    if result != 200:
                        print(f"Programa {json_item['title']} - 'download_url' {url}, error {result} ")
        
    print(f"Processed {len(items)} items")


def main():
    print("Converts a WordPress export to a JSON usable dataset")
    logging.basicConfig(filename="rebost-links.log", level=logging.DEBUG, filemode="w")
    check_links("raw/programes.xml")

if __name__ == "__main__":
    main()