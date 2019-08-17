# filename: poliplotter.py

import re # used to clean tweets
import tweepy # used in API authorization and uploading to bot
import secrets # used for Twitter APIs
import datetime # used for inserting day of the week into status
import numpy as np # used for interpreting the mask images
from PIL import Image # used to open the mask images
from textblob import TextBlob # used to parse individual words
import matplotlib.pyplot as plt # used to help plot word cloud and save image to file
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator # used to generate word cloud and remove stopwords

def authenicator():
    """creates the authenication object, sets access token and secret, then creates the tweepy API object to fetch and upload tweets"""
    try:
        auth = tweepy.OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
        auth.set_access_token(secrets.access_token, secrets.access_token_secret)
        api = tweepy.API(auth)
    except:
        print("\nError: Authentication Failed\n")
        quit()
    return api

def target_user():
    """accepts two inputs from user and sets tweet status"""
    name = input("\nWithout including the @ symbol,\nPlease type the username of the requested account: ")
    tweetCount = int(input("How many tweets would you like to analyze? "))
    day_of_week = datetime.date.today().strftime("%A")
    status = f"Happy {day_of_week}! Here's how @{name} spent the past week on Twitter!"
    return name, tweetCount, status

def results(api, name, tweetCount):
    """gathers x number of tweets from the user and returns the results"""
    results = api.user_timeline(id=name, count=tweetCount, tweet_mode="extended")
    return results

def compiler(results):
    """cycles through full results, checks against RTs and then adds the rest to one complete string"""
    tweet_string = ""
    for tweet in results:
        full_tweet = tweet.full_text
        if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
            tweet_string += full_tweet
    return tweet_string

def clean_tweet(tweets):
    """Uses regex statements to clean tweets by removing links and special characters"""
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweets).split())

def string_prep(clean_tweets):
    """prepares the tweets for later use by the wordcloud function"""
    tweet_words = TextBlob(clean_tweets) # allows for tweets to be manipulated
    words = tweet_words.words # creates a WordList
    word_string = " ".join(words) # joins as one string
    return word_string

def stopwords():
    """establishes stopwords and adds on some custom ones"""
    stopwords = set(STOPWORDS)
    stopwords.update(["amp", "will", "need", "much", "us", "Im", "cant", "going", "thats"])
    return stopwords

def assign_mask(name):
    """assigns corresponding mask based on Twitter user"""
    user_image_dict = {"realdonaldtrump": "img/trump_portrait.jpg", "joebiden": "img/biden_flag.webp", "berniesanders": "img/bernie_flag.jpg", "senwarren": "img/warren_flag.jpeg", "kamalaharris": "img/kamala_flag.jpg", "petebuttigieg": "img/pete_flag.jpg"}
    for user, user_image in user_image_dict.items():
        if user == name:
            image_loc = user_image
    if name not in user_image_dict:
        print(f"\nWe're sorry. There is either no available image for '{name}' or '{name}' is not a valid Twitter user. Please try again.\n")
        quit()
    mask = np.array(Image.open(image_loc)) # opens the image file, converts to a NumPy array and stores as the "mask" variable
    return mask

def wordcloud(word_string, stopwords):
    """creates the wordcloud object"""
    try:
        wc = WordCloud(stopwords=stopwords, background_color="white", max_words=10000, mask=mask).generate(word_string)
        return wc
    except ValueError:
        print(f"We're sorry. '{name}' is not a valid Twitter user.\n")
        quit()

def save(mask, wc):
    """creates color from the image, sets size and other image features, then saves the generated image"""
    image_colors = ImageColorGenerator(mask)
    plt.figure(figsize=[16,9])
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    plt.savefig("poliplotpics/poliplotpic.png")

if __name__ == '__main__':
    api = authenicator()
    name, tweetCount, status = target_user()
    results = results(api, name, tweetCount)
    tweet_string = compiler(results)
    clean_tweets = clean_tweet(tweet_string)
    word_string = string_prep(clean_tweets)
    stopwords = stopwords()
    mask = assign_mask(name)
    wc = wordcloud(word_string, stopwords)
    save(mask, wc)
    api.update_with_media("poliplotpics/poliplotpic.png", status) # sends status and word cloud image to Twitter bot
