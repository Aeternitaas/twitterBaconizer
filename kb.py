# coding: utf-8
from twython import Twython
from pprint import pprint
from sklearn.feature_extraction.text import TfidfVectorizer as TfidfVect
import json
import sys
import re

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
        # print("Text" + text.encode('unicode_escape').decode('ascii', 'ignore')) #TODO: Debugging

    text = text.encode('unicode_escape').decode('ascii', 'ignore')    # decode Unicode-only characters.
    wordList = re.split( '[: ]', text )

    for word in wordList:
        if len(word) > 1 and word[0] == '@':
            print("Adding:", word) 
            handleList.append( (word, text) )
    
    return handleList

def getRecentBacon():
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
    vect = TfidfVect(min_df=1)
    tfidf = vect.fit_transform(tweetList)
    return (tfidf * tfidf.T).A

def main():
    traversed = {}
    baconString = ""

    # takes the twitter handle and queries it through the Twitter
    # API.
    query = "from:%s" % sys.argv[1]
    search = twitter.search(q=query, tweet_mode='extended')

    # obtains the most upvoted recent tweet/retweet
    baconString = getRecentBacon()
    print( "Bacon String: " + baconString )

    for j in range( 0, 1 ):
        handleList = []

        # parse mentions of starting user.
        for i in range( 0, len(search["statuses"]) ):
            status = search["statuses"][i]
            pprint( status )
            # handleList.extend( getHandles( status["full_text"] ) )
            handleList.extend( getHandles( status ) )

        # print(handleList)

        for i in range( 0, len(handleList) ):
            print( handleList[i][1] )
            print( checkSimilarity( [baconString, handleList[i][1]] ) )

        if "@kevinbacon" in handleList:
            print("Finished!")
            return 0

if __name__ == '__main__': 
    main()
