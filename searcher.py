import socket
import psycopg2
import json
import getopt
import sys

class IndexSearcher:
    def __init__(self):
        pass

    def hitIndex(self, host, port, query):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((str(host), int(port)))
        # send the json request for a socket
        s.send(json.dumps({'query': str(query)}))
        # tell the other end of the socket that I'm done writing
        s.shutdown(socket.SHUT_WR)
        #recieve the response
        try:
            data = bytes()
            while True:
                new_data = s.recv(1024)
                if not new_data: break
                data += new_data
            s.close()
            s = None
            data = str(data)
        except Exception as e:
            print e

        print data
        data_obj = {}
        try:
            data_obj = json.loads(data)
        except Exception as e:
            print e

        if 'worked' not in data_obj or data_obj['worked'] == False:
            print 'DID NOT WORK ' + host + ':' + str(port) + '?' + query

        if 'posts' not in data_obj:
            print 'MISSING POSTS'

        return data_obj['posts']

    def getPostsFromTagIndex(self, tag):
        port = 7777
        host = 'localhost' # searcher runs on helix
        post_ids = self.hitIndex(host, port, tag)
        return post_ids

    def getPostsFromTitleIndex(self, query):
        port = 7778
        host = 'helix.vis.uky.edu'
        post_ids = self.hitIndex(host, port, query)
        return post_ids

    def getPostsFromQuery(self, query):
        # split by words
        words = query.split(' ')
        post_ids = set()
        if len(words) == 1:
            post_ids = set(self.getPostsFromTagIndex(query))
        else:
            # the intersection of post_ids from individual words
            post_ids = []
            for word in words:
                post_ids_for_word = self.getPostsFromTagIndex(word)
                post_ids = list(set(post_ids) & set(post_ids_for_word))
            
            # the entire query itself
            post_ids_for_whole_query = self.getPostsFromTagIndex(query)
            post_ids = set(post_ids + post_ids_for_whole_query)
        return post_ids
    
def getPostsFromDatabase(post_ids):
    conn_string = "host='helix.vis.uky.edu' dbname='cs585' user='cs585' password='shamblr'"
    
    rows = []
    try:
        db_conn = psycopg2.connect(conn_string)
        cursor = db_conn.cursor()
        ids = tuple(list(post_ids))
        cursor.execute("SELECT * FROM post WHERE post_id IN %s; ",(ids,))
        rows = cursor.fetchall()
    except Exception as e:
        print e

    posts = []
    for row in rows:
        post = {
            'post_id': row[0],
            'url': row[1],
            'blog_name': row[2],
            'type': row[3],
            'content': row[4],
            'date': str(row[5]),
            'num_notes': row[6],
            'title': row[7]
        }
        posts.append(post)
    return posts

# the main searcher!
def handleQuery(query):
    index = IndexSearcher()
    post_ids = index.getPostsFromQuery(query.lower())

    # now rank them

    # we need to limit DB extraction to the actual results.
    print post_ids
    posts = getPostsFromDatabase(post_ids)
    print posts
    return posts

# the infinite workhorse
def main(test_first):
    if test_first:
        while True:
            s = str(raw_input('test query: '))
            if s == '':
                break
            print 'finding : ' + s

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost',7776))
        s.listen(1)

        conn = None
        while True:
            conn, address = s.accept()
            data = bytes()
            while True:
                new_data = conn.recv(1024)
                if not new_data:
                    break
                data += new_data
            data = str(data)

            data_obj = {}
            try:
                data_obj = json.loads(data)
            except Exception as e:
                print "Error handling JSON loading"
                print e
            
            response = dict()
            response['worked'] = True
            response['posts'] = []

            try:
                response['posts'] = handleQuery(data_obj['query'])
            except Exception as e:
                print e

            print "Ready to send"
            conn.send(json.dumps(response))
            conn.shutdown(socket.SHUT_WR)
            if conn != None:
                conn.close()
                conn = None
            print "done"

    except Exception as e:
        print "Exception in main socket loop"
        print e

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t", ["test"])
    except getopt.GetoptError:
        print "Failed to get command line arguements"

    # if you want to run manual queries on the searcher 
    # before you start the socket loop, run with --test
    test_first = False
    for opt, arg in opts:
        if opt in ('-t','--test'):
            test_first = True

    handleQuery('barack obama')
    #main(test_first)
