# coding: utf-8
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

twitter =  Twython(consumer_key, consumer_secret,
                    access_token, access_token_secret)

def getHandles( tweet ):
    '''
    params:

    returns: the list of all twitter handles.
    '''
    wordList, handleList = [], []
    quotedStatus = ""
    text = tweet["full_text"]

    if "quoted_status" in tweet:
        quotedStatus = tweet["quoted_status"]["full_text"]
        quotedStatus = re.sub(r'@[A-Za-z0-9]', '', quotedStatus, flags=re.MULTILINE)
        text = text + " " + quotedStatus + " @" + tweet["quoted_status"]["user"]["screen_name"]
        # print("Text" + text.encode('unicode_escape').decode('ascii', 'ignore')) # TODO: Debugging

    elif "retweeted_status" in tweet:
        quotedStatus = tweet["retweeted_status"]["full_text"]
        quotedStatus = re.sub(r'@[A-Za-z0-9]', '', quotedStatus, flags=re.MULTILINE)
        text = text + " " + quotedStatus + " @" + tweet["retweeted_status"]["user"]["screen_name"]
        # print("Text" + text.encode('unicode_escape').decode('ascii', 'ignore')) # TODO: Debugging

    text = text.encode('unicode_escape').decode('ascii', 'ignore')    # decode Unicode-only characters.
    wordList = re.split( '[: ]', text )

    for word in wordList:
        if len(word) > 1 and word[0] == '@':
            # print("Adding:", word)  #TODO: REMOVE
            handleList.append( (word, text) )
    
    return handleList

def getRecentBacon():
    '''
    
    '''
    query = "from:%s" % "@kevinbacon"
    search = twitter.search(q=query, tweet_mode='extended')

    quotedStatus = ""
    quotedFavoriteCount = 0

    tweetList = []

    for i in range( 0, len(search["statuses"]) ):
        status = search["statuses"][i]
        # pprint( status )

        if "quoted_status" in status:
            quotedStatus = status["quoted_status"]["full_text"]
            quotedfavoriteCount = status["quoted_status"]["favorite_count"]
        elif "reweeted_status" in status:
            quotedStatus = status["retweeted_status"]["full_text"]
            quotedfavoriteCount = status["retweeted_status"]["favorite_count"]

        tweetList.append( (status["favorite_count"] + quotedFavoriteCount, status["full_text"] + " " + quotedStatus) )
    
    tweetList.sort()

    # retrieve post with highest favourite count
    tweet = (max( tweetList ))[1]

    # strip http links
    tweet = re.sub(r'https\S+', '', tweet, flags=re.MULTILINE)

    return tweet

def checkSimilarity( tweetList ):
    '''
    params:
        tweetList - 

    returns:
    '''
    vect = TfidfVect(min_df=1)
    tfidf = vect.fit_transform(tweetList)
    return ((tfidf * tfidf.T).A)[0][1]

def findBacon( search, baconString, traversed, depth ):
    '''
    params:
        search
        baconString
        traversed
    '''
    query = "from:%s" % search
    search = twitter.search(q=query, tweet_mode='extended')
    pq = []
    depth -= 1

    # for j in range( 0, 1 ):
    while True:
        handleList = []

        # parse a tuple of (mentions, tweet) of starting user.
        for i in range( 0, len(search["statuses"]) ):
            status = search["statuses"][i]
            # pprint( status )                                       #TODO: REMOVE
            # handleList.extend( getHandles( status["full_text"] ) ) #TODO: REMOVE
            handleList.extend( getHandles( status ) )

        # check if @kevinbacon is mentioned inside of the handleList 
        if "@kevinbacon" in handleList:
            print("Finished!")
            break

        if depth == 0:
            break

        if len(handleList) == 0:
            break

        # print(handleList) # TODO: REMOVE

        # create a PQ from the similarity values, associating them with a handle
        for i in range( 0, len(handleList) ):
            similarity = checkSimilarity( [baconString, handleList[i][1]] )
            # print(str(similarity) + " " + str(handleList[i][1])) # TODO: REMOVE
            heapq.heappush( pq, (similarity * -1, handleList[i][0] ) )

        while len(pq) > 0:
            nextTuple = (heapq.heappop(pq))
            nextSimilarity = nextTuple[0] * -1
            nextHandle = nextTuple[1]
            # if nextHandle not in traversed:
            if nextHandle not in traversed and nextSimilarity > .2:
                traversed[nextHandle] = True
                print("Traversing... " + nextHandle)
                sys.stdout.flush()
                findBacon( nextHandle, baconString, traversed, depth )

    return

def main():
    depth = 1000
    baconString = ""
    traversed = {}

    # takes the twitter handle and queries it through the Twitter
    # API.
    query = "from:%s" % sys.argv[1]
    search = twitter.search(q=query, tweet_mode='extended')

    # ensure that we don't re-traverse the start.
    traversed[sys.argv[1]] = True

    # obtains the most upvoted recent tweet/retweet
    baconString = getRecentBacon()
    print( "Bacon String: " + baconString + "\n" )

    findBacon( sys.argv[1], baconString, traversed, depth )

    return

if __name__ == '__main__': 
    main()
