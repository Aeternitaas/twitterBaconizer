from twython import Twython
from pprint import pprint
import json
import sys

# enter your keys, and tokens obtained from your twitter app
consumer_key="VjDIekyHP11VGZA7dIYSCRWkt"
consumer_secret="NomxYPB8XMhjrELdaX5kg1UHWb32jvxFAzu9L95a50ADoidmOE"
access_token="4113456820-XANkYBXvdIZ4ckPVNQkL28mR32tXdHt6cHn7DRZ"
access_token_secret="fwE9ZtnYswd8hFUAjP2qaVfR4gsgDie62YnE6kZefm7cm"


twitter =  Twython(consumer_key, consumer_secret,
                    access_token, access_token_secret)

def getHandles( text ):
    wordList = []
    handleList = set()
    wordList = text.split()

    for i in wordList:
        if i[0] == '@' and len(i) > 1:
            handleList.add(i)
    
    return handleList

def main():
    query = "from:%s" % sys.argv[1]
    x = twitter.search(q=query)
    
    # pprint( x[ "statuses" ] )

    for j in range( 0, 1 ):
        handleSet = set()
        for i in range( 0, len(x["statuses"]) ):
            status = x["statuses"][i]
            # pprint( status["text"] )
            handleSet.update( getHandles( status["text"] ) )
        print handleSet

if __name__ == '__main__': 
    main()
