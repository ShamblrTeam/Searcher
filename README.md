Run with Python 2.7

HOW TO USE THE SEARCHER 
==============

It is currently running on port 7776 on helix.vis.uky.edu. You pass a json `{'query':'yolo'}` object with your query. It will return a json object '' with the `post_id`s. Consult `test_socket.py` for an example.


SETUP
=========

`python searcher.py` will load and start the searcher index on port 7776

`python searcher.py --test` loads the data, but then allows you to play around with testing it via input. Press enter on an empty input to start the sockets.

Run `python test_socket.py` to test the socket.

Run `sh monitor.sh searcher.py` to use the monitoring script for the searcher. This will restart the searcher on fail.
