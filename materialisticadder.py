import json
from pathlib import Path
import argparse
import time
import random
import string

# List of url in bookmarks
url = []

# List of id and guid
idbm = []
guid = []

# List of the new children
newdict = []



def generateuniques():
    newtime = int(time.time()*10**6)
    newid = random.randint(1,10**5)
    while newid in idbm:
        newid = random.randint(1,10**5)
    idbm.append(newid)
    newguid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    while newguid in guid:
        newguid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    guid.append(newguid)
    return (newtime, newid, newguid)

def extracturl(element):
    "Input is a dict, add to "
    for i in element:
        if 'children' in i:
            extracturl(i['children'])
        if 'uri' in i:
            url.append(i['uri'])
        if 'id' in i:
            idbm.append(i['id'])
        if 'guid' in i:
            guid.append(i['guid'])

def populatedict(uri, title):
    (newtime,newid,newguid) = generateuniques()
    new = {'guid': newguid,
   'title': title,
   'index': 4,
   'dateAdded': newtime,
   'lastModified': newtime,
   'id': newid,
   'typeCode': 1,
   'charset': 'UTF-8',
   'type': 'text/x-moz-place',
   'uri': uri}
    newdict.append(new)

if __name__ == '__main__':
    home = str(Path.home())
    parser = argparse.ArgumentParser()
    parser.add_argument("pathbm", help = "Full path from $HOME of bookmarks that will updated")
    parser.add_argument("materialistic", help = "Full path from $HOME of file used for updating")
    parser.add_argument("destination", help = "Full path from %HOME of new bookmarks")
    args = parser.parse_args()
    with open('%(home)s/%(path)s' %{'home':home,'path': args.pathbm}) as fp:
        bookmarks = json.loads(fp.read())
    # First level is __root
    bm = bookmarks['children']
    tmp = []
    # Every element of bm is a different position (menu, toolbar, unfiled,mobile)
    for i in range(0,len(bm)):
        if 'children' in bm[i]:
            extracturl(bm[i]['children'])
    # Create the folder
    (newtime,newid,newguid) = generateuniques()
    folder = {'guid':'0','title':'backup','index': 0,'dateAdded': newtime, 'lastModified': newtime, 'id': newid, 'typeCode': 2,
 'type': 'text/x-moz-place-container'}
    # Generate the list of new urls
    with open('%(home)s/%(path)s' %{'home':home,'path': args.materialistic}) as fp:
        newurl = fp.readlines()
    i = 0
    while i < len(newurl):
        if newurl[i] == '\n':
            del newurl[i]
        else:
            i += 1
    del newurl[1::3]
    newtitle = newurl[0::2]
    del newurl[0::2]
    for i in range(len(newurl)):
        newurl[i]=newurl[i][:-1]
        newtitle[i]=newtitle[i][:-1]
    i = 0
    while i < len(newurl):
        if newurl[i] in url:
            del newurl[i]
            del newtitle[i]
        else:
            populatedict(newurl[i], newtitle[i])
            i += 1
    folder['children'] = newdict
    bookmarks['children'][1]['children'].append(folder)
    with open('%(home)s/%(path)s/destination.json' %{'home':home,'path': args.destination}, 'w') as fp:
        json.dump(bookmarks,fp)
    
