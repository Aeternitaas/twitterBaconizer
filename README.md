# twitterBaconizer

Searches for a path to Twitter mentions of Kevin Bacon through any series of @ mentions, retweets, and quotes.

Utilizes a Depth-Limited Best-First Search scheme, utilizing tf-idf string comparisons to measure similarity of tweets between Kevin Bacon and the origin user to determine the best path forward. 

## Dependencies

Uses numpy, scipy, and scikit-learn for Tf-Idf Vectorization.

## Usage

Before using this, proper authentication must be obtained from apps.twitter.com, specifically the consumer key and consumer secret keys for OAUTH2, and access tokens and access token secret if you wish to use OAUTH1 (polling limits will be reduced to 180 requests per 15 minutes however.)

```
$ python2.7 kb.py twitter_handle
```
