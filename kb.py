# coding: utf-8
# Author: Ket-Meng Jimmy Cheng
# - "Six" Degrees of Kevin Bacon
#
#   Attempts to search for the 90's heartthrob Kevin Bacon through twitter mentions.
# It, however, makes no attempt to minimize the distance, rather it simply looks for any
# path using a Depth-limited, Best-First Search.

from twython import Twython
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer as TfidfVect
import json
import time 
import sys
import re
import heapq

# enter your keys, and tokens obtained from your twitter app
consumer_key="VjDIekyHP11VGZA7dIYSCRWkt"
consumer_secret="NomxYPB8XMhjrELdaX5kg1UHWb32jvxFAzu9L95a50ADoidmOE"
access_token="4113456820-XANkYBXvdIZ4ckPVNQkL28mR32tXdHt6cHn7DRZ"
access_token_secret="fwE9ZtnYswd8hFUAjP2qaVfR4gsgDie62YnE6kZefm7cm"

# twitter =  Twython(consumer_key, consumer_secret,
                    # access_token, access_token_secret)

# Used OATH2 for more polling.
twitter = Twython(consumer_key, consumer_secret, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(consumer_key, access_token=ACCESS_TOKEN)

def getHandles( tweet ):
    '''
    Obtains parses a list twitter handles and forms tuples that associate twitter handles with their associated tweet text.

    params:
        - tweet : a single tweet and its metadata made by a person.

    returns: the list of all twitter handles and their associated tweet contents.
    '''
    wordList, handleList = [], []
    quotedStatus = ""

    text = tweet["full_text"]   # text of the original tweet
    tweetID = tweet["id_str"]   # tweet ID of the original tweet

    # if it is a quote, obtain quoted_status's text.
    if "quoted_status" in tweet:
        text = getSubtweet( text, tweet, "quoted_status" )

    # if it is a retweet, obtain retweeted_status's text.
    elif "retweeted_status" in tweet:
        text = getSubtweet( text, tweet, "retweeted_status" )

    # convert all to lowercase and decode/encode utf-8.
    text = text.lower()
    text = text.encode('unicode_escape').decode('ascii', 'ignore')    

    # splits by spaces and colons to find handle easily.
    wordList = re.split( '[:\'\"\n_,.!? ]', text )

    # generate list of tuples in the form of (handle, tweet text, tweet ID).
    for word in wordList:
        if len(word) > 1 and word[0] == '@':
            handleList.append( (word, text, tweetID) )
    
    return handleList

def getSubtweet( text, tweet, subType ):
    '''
    Obtains subtweets from quoted_status and retweeted_status and strips handles.

    args:
        - text : the tweet text of the original tweeter.
        - tweet : the tweet metadata.
        - subType : the type of subtweet (quoted_status vs retweeted_status)

    returns: the concatenation of the original text and the subtweeted text.
    '''
    subStatus = tweet[subType]["full_text"]
    # remove @ handles from retweets to prevent traversing those paths as well.
    subStatus = re.sub(r'@[A-Za-z0-9]', '', subStatus, flags=re.MULTILINE)
    text = text + " " + subStatus + " @" + tweet[subType]["user"]["screen_name"]

    return text

def getRecentBacon():
    '''
    Finds the most recent posts made by Kevin Bacon, with the additional measure of concatenating retweets and quotes
    with the original text. Then returns the post with the most favourites.

    returns: the concatenated tweet with the most favourites.
    '''
    query = "from:%s" % "@kevinbacon"
    search = twitter.search(q=query, tweet_mode='extended')

    quotedStatus = ""
    quotedFavoriteCount = 0

    tweetList = []

    # search through recent tweets to generate a list of favourite:tweet_text associations in the form of tuples.
    for i in range( 0, len(search["statuses"]) ):
        status = search["statuses"][i]

        if "quoted_status" in status:
            quotedStatus = status["quoted_status"]["full_text"]
            quotedfavoriteCount = status["quoted_status"]["favorite_count"]
        elif "reweeted_status" in status:
            quotedStatus = status["retweeted_status"]["full_text"]
            quotedfavoriteCount = status["retweeted_status"]["favorite_count"]

        tweetList.append( (status["favorite_count"] + quotedFavoriteCount, status["full_text"] + " " + quotedStatus) )
    
    # retrieve post with highest favourite count.
    tweet = (max( tweetList ))[1]

    # strip https links that are appended to full_text.
    tweet = re.sub(r'https\S+', '', tweet, flags=re.MULTILINE)

    return tweet.lower()

def checkSimilarity( tweetList ):
    '''
    Uses TfidfVectorizer from scikit-learn to calculate similarities in sentences. 

    params:
        tweetList - tweets to be compared.

    returns: the percentile value of similarity between tweets.
    '''
    vect = TfidfVect(min_df=1)
    tfidf = vect.fit_transform(tweetList)
    return ((tfidf * tfidf.T).A)[0][1]

def printPath( pathList, search, status ):
    '''
    Prints the path traversed to a goal handle.
    '''
    for i in range( 0, len(pathList) ):
        print(pathList[i])

    print( search + ", " + str(status["id_str"]) + ", " + str(status["full_text"]) )

    return

def findBacon( searchName, baconString, traversed, depth, pathList ):
    '''
    Recursive function for finding Kevin Bacon that performs a Depth-Limited DFS.

    params:
        search - the twitter handle to be searched.
        baconString - Bacon's most recent and favourited tweet to be compared to.
        traversed - the list of traversed nodes/handles.
        depth - the maximum depth allowed to be travelled.
        pathList - the path traversed.
    '''
    # twitter search setup 
    query = "from:%s" % searchName
    search = twitter.search(q=query, tweet_mode='extended')

    pq, handleList = [], []
    regexp = re.compile(r'@?[k|K]evin[ ]?[b|B]acon')
    newPathList = list(pathList)
    depth -= 1

    # base cases:
    if depth == 0:
        return 
    if not search["statuses"]:
        return

    # parse a tuple of (mentions, tweet) of starting user.
    for i in range( 0, len(search["statuses"]) ):
        status = search["statuses"][i]
        if regexp.search(status["full_text"]):
            print("Finished!")
            printPath( pathList, searchName, status )
            return 
        handleList.extend( getHandles( status ) )

    # if the person doesn't have any recent mentions, stop.
    if len(handleList) == 0:
        return 

    # create a PQ from the similarity values, associating them with a handle
    for i in range( 0, len(handleList) ):
        if handleList[i][0] not in traversed:
            similarity = checkSimilarity( [baconString, handleList[i][1]] )
            heapq.heappush( pq, (similarity * -1, handleList[i][0], handleList[i][1], handleList[i][2] ) )  # pushes a tuple in the form of (similarity, word, text, tweetid).

    # empty the priority queue by its similarity number
    while pq:
        nextTuple = (heapq.heappop(pq))
        nextSimilarity = nextTuple[0] * -1  # since heapq is a minheap, convert it back to a positive number.
        nextHandle = nextTuple[1]
        nextText = nextTuple[2]
        nextId = nextTuple[3]

        print( "Trying handle... " + nextHandle ) 
        sys.stdout.flush()

        if nextHandle not in traversed:
            traversed[nextHandle] = True    # mark as traversed

            print( "Traversing... " + nextHandle ) 
            print( str(nextSimilarity) + " " + nextText )
            sys.stdout.flush()

            # create a new instance of a pathList to record the path to Kevin Bacon
            newPathList = list(pathList)
            newPathList.append( searchName + ", " + nextId + ", " + nextText )
            time.sleep(5)                   # prevents overpolling
            findBacon( nextHandle, baconString, traversed, depth, newPathList )

            print("Finished traversing... " + nextHandle)
            sys.stdout.flush()

    print("Ending depth... " + str(depth))
    sys.stdout.flush()

    return

def main():
    depth = 1000
    baconString = ""
    traversed = {}

    # takes the twitter handle and queries it through the Twitter API.
    query = "from:%s" % sys.argv[1]
    search = twitter.search(q=query, tweet_mode='extended')

    # ensure that we don't re-traverse the start.
    traversed[sys.argv[1]] = True

    # obtains the most upvoted recent tweet/retweet
    baconString = getRecentBacon()
    print( "Bacon String: " + baconString + "\n" )

    # begin the search process.
    findBacon( sys.argv[1], baconString, traversed, depth, [] )

    return

if __name__ == '__main__': 
    main()
