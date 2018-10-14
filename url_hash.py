import argparse
import numpy as np
golden_ratio = np.uint32(0x9E3779B9)

def rotate_left(value):
    return np.uint32((value <<5) | (value >> 27)) 

def add_to_hash(hash,value):
    return np.uint32(golden_ratio*((rotate_left(hash)) ^ ord(value)))

def hash_simple(url, l):
    h = 0
    for i in range(l):
        h = add_to_hash(h,url[i])
    return np.uint32(h)
def url_hash(url):
    l = len(url)
    pref = -1
    i=0
    for i in range(l):
        if url[i] == ':':
            pref = i
            break
    return str(np.uint64(((hash_simple(url,pref) & 0x0000FFFF) << 32)) + np.uint64(hash_simple(url,l)))


if __name__=="__main__":
    url = "https://example.org/"
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Url to moz_hash")
    print(url_hash(parser.parse_args().url))
