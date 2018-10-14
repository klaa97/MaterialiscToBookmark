import json
import argparse
import time
from pathlib import Path
import random
import string
import sqlite3
from url_hash import url_hash

# List of url in bookmarks
url = []

# List of id and guid
idbm = []
guid = []

# List of the new children
newdict = []
def revhost(url):
    try: 
        return url.split('//')[1].split('/')[0][::-1] 
    except Exception:
        return '.'

def generateuniques(choice = 1,guid =guid):
    newtime = int(time.time()*10**6)
    newguid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    while newguid in guid:
        newguid = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    guid.append(newguid)
    if choice == 1:
        newid = random.randint(1,10**5)
        while newid in idbm:
            newid = random.randint(1,10**5)
        idbm.append(newid)
        return (newtime, newid, newguid)
    else:
        return (newtime,newguid)
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
def generateurls(home, args):
    # Generate the list of new urls and titles
    with open('%(home)s/%(path)s' %{'home':home,'path': args.paths[1]}) as fp:
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
    return newurl,newtitle
def jsonupdate(args):
    home = str(Path.home())
    with open('%(home)s/%(path)s' %{'home':home,'path': args.paths[0]}) as fp:
        bookmarks = json.loads(fp.read())
    # First level is __root
    bm = bookmarks['children']
    # Every element of bm is a different position (menu, toolbar, unfiled,mobile)
    for i in range(0,len(bm)):
        if 'children' in bm[i]:
            extracturl(bm[i]['children'])
    # Create the folder
    (newtime,newid,newguid) = generateuniques()
    folder = {'guid':newguid,'title':'backup','index': 0,'dateAdded': newtime, 'lastModified': newtime, 'id': newid, 'typeCode': 2,
    'type': 'text/x-moz-place-container'}
    newurl,newtitle = generateurls(home,args)
    while i < len(newurl):
        if newurl[i] in url:
            del newurl[i]
            del newtitle[i]
        else:
            populatedict(newurl[i], newtitle[i])
            i += 1
    folder['children'] = newdict
    bookmarks['children'][1]['children'].append(folder)
    with open('%(home)s/%(path)s/destination.json' %{'home':home,'path': args.paths[2]}, "w+") as fp:
        json.dump(bookmarks,fp)
def sqlupdate(args):
    home = str(Path.home())
    conn = sqlite3.connect('{}'.format(args.paths[0])) 
    conn.create_function("revhost",1,revhost)
    c = conn.cursor()
    # bm - "parent" is the "id" of the folder that contains the element,toolbar is 3
    # bm - id is consecutive, fk is the key to reference in moz_places, folder is type 2
    # Scrape the urls and titles
    titleurl = c.execute("SELECT moz_bookmarks.title, moz_places.URL FROM moz_bookmarks JOIN moz_places on MOZ_bookmarks.fk = moz_places.id").fetchall()
    url = [i[1] for i in titleurl]
    # Find the max id
    parent = c.execute("SELECT max(id) FROM moz_bookmarks").fetchone()[0] +1
    guid = [i[0] for i in c.execute("SELECT guid FROM moz_bookmarks").fetchall()]
    newidbm = parent+1 
    newtime, newguid = generateuniques(0,guid)
    position = c.execute("SELECT max(position) FROM moz_bookmarks WHERE parent = 3")
    #c.execute("INSERT INTO moz_bookmarks VALUES (?,2,NULL,3,0,'backup',NULL,NULL,?,?,?,'0','1')",[parent,newtime,newtime,newguid])
    #conn.commit()
    newurl,newtitle = generateurls(home,args)
    i = 0
    position = 0
    newidplace = c.execute("SELECT max(id) FROM moz_places").fetchone()[0] +1
    while i < len(newurl):
        if newurl[i] in url:
            del newurl[i]
            del newtitle[i]
        else:
            print("adding")
            newtime, newguid = generateuniques(0,guid)
            c.execute("INSERT INTO moz_places VALUES (?,?,NULL,?,0,0,0,100,NULL,?,1,?,NULL,NULL,2)",[newidplace,newurl[i],revhost(newurl[i]),newguid,url_hash(newurl[i])])
            c.execute("INSERT INTO moz_bookmarks VALUES (?,1,?,?,?,?,NULL,NULL,?,?,?,0,1)",[newidbm,newidplace,parent,position,newtitle[i],newtime,newtime,newguid])
            i += 1
            newidbm+=1
            newidplace+=1
            position+=1  
    conn.commit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers= parser.add_subparsers()
    parser_sql = subparsers.add_parser('sql', help="update sqlite .places database, using as arguments (in order): path to DB, full path to Materialistic backup")
    parser_json = subparsers.add_parser('json', help = "create a new json file with bookmarks to import, using as arguments (in order), path from $HOME: full path to json backup, full path to Materialistic backup, full path to destination")
    parser_sql.add_argument('paths', nargs=2)
    parser_json.add_argument('paths', nargs = 3)
    parser_sql.set_defaults(func=sqlupdate)
    parser_json.set_defaults(func=jsonupdate)
    #parser.add_argument("path", help = "Full path from $HOME of bookmarks/sqlite DB that will updated")
    #parser.add_argument("materialistic", help = "Full path from $HOME of file used for updating")
    #parser.add_argument("destination", help = "Full path from %HOME of new bookmarks")
    args = parser.parse_args()
    args.func(args)