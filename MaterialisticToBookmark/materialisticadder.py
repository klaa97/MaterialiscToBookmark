import json
from pathlib import Path

# List of url in bookmarks
url = []

def extracturl(element):
    "Input is a dict, output is the list of links"
    children = 'children'
    uri = 'uri'
    for i in element:
        if children in i:
            extracturl(i[children])
        elif uri in i:
            url.append(i['title'])

if __name__ == '__main__':
    home = str(Path.home())
    with open('%(home)s/Desktop/bookmarks-2018-08-15.json' %{'home':home}) as fp:
        bm = json.loads(fp.read())
    # First level is __root
    bm = bm['children']
    tmp = []
    # Every element of bm is a different position (menu, toolbar, unfiled,mobile)
    for i in range(0,len(bm)):
        if 'children' in bm[i]:
            extracturl(bm[i]['children'])
    

    

