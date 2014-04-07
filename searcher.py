import socket
import json

def hitIndex(host, port, query):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # send the json request for a socket
    s.send(json.dumps({'query': query}))
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

def getPostsFromTagIndex(tag):
    port = 7777
    host = 'helix.vis.uky.edu'
    post_ids = hitIndex(port, host, tag)
    return post_ids

def getPostsFromTitleIndex(query):
    port = 7778
    host = 'helix.vis.uky.edu'
    post_ids = hitIndex(port, host, query)
    return post_ids

# the main searcher!
def handleQuery(query):
    query = query.lower()

    post_ids = getPostsFromTagIndex(query)



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
        s.bind(('',7776))
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

            print "Working with:"
            print data_obj 

            
            
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

    main(test_first)
