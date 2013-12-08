#!/usr/bin/python3
# coding:utf-8
"""
_________________________________________________
 _____          _ _   ____        _   _      
|_   _|_      _(_) |_| __ ) _   _| |_| |_ __ 
  | | \ \ /\ / / | __|  _ \| | | | __| | '__|
  | |  \ V  V /| | |_| |_) | |_| | |_| | |   
  |_|   \_/\_/ |_|\__|____/ \__,_|\__|_|_|   3.3
_________________________________________________

by lesguillemets.

Twitter-based butler. Just for you.
"""

from twython import Twython as tw
import time
import os
import random
from html.parser import HTMLParser

from keys import *
from modules import *

pwd = os.path.dirname(__file__)
LAST_READ_FILE = os.path.join(pwd, "lastread.txt")


class Butlr(object):
    
    def __init__(self):
        self.t = tw(CONSUMER_KEY, CONSUMER_SECRET,
                    ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        with open(LAST_READ_FILE, 'r') as f:
            self.last_read = int(f.read().strip())
        
        self.commands = {
            'wp' : self.wikipedia,
            'rgb' : self.rgb,
            'bf' : self.bf,
            'randc' : self.randc,
            'ping' : self.ping,
            'weather' : self.weather,
        }
    
    def update(self):
        print(time.strftime("%H:%M:%S--%d%b%Y (%a)"))
        
        replies = self.t.get_mentions_timeline(since_id=self.last_read)
        
        if replies: # if there's been any replies since last time
            
            # begin updating last read records
            self.last_read = replies[0]['id_str']
            
            print("Read from: id {} with text : {} | from @{}. read {} items".format(
                self.last_read, replies[-1]['text'],
                replies[-1]['user']['screen_name'],
                len(replies)))
            with open(LAST_READ_FILE, 'w') as f:
                f.write(self.last_read)
            
            # execute each commands
            for reply in replies:
                self.order(reply)
        else:
            print("No new replies.")
        
        print("____________________")
    
    def order(self, tweet):
        command = tweet['text'].split()[1]
        try: # known commands
            self.commands[command](tweet)
        except KeyError: 
            # command not found, or 
            # calling commands with ambiguous name
            if command[-2:] == 'wp' and len(command) == 4:
                self.wikipedia(tweet)
            else:
                self.cmd_not_found(command)
    
    def cmd_not_found(self, command):
        pass
    
    #########################
    #       commands        #
    #########################
    
    def wikipedia(self, tweet):
        text = tweet['text'].split()[1:]
        langcode = text[0][:-2]
        articlename = '_'.join(text[1:])
        username = tweet['user']['screen_name']
        
        res = wparticle.wparticle(langcode, articlename)
        
        if res[0]: # if article is found:
            # update tweet
            self.t.update_status(status = "@{} {}".format(username, res[1]),
                                 in_reply_to_status_id = tweet['id'])
            # log
            print("replied to {} for {}wp, {}".format(
                        username, langcode, articlename))
        
        else: # no matching article!
            self.t.update_status(status = "@{} {}".format(username, res[1]),
                                 in_reply_to_status_id = tweet['id'])
            print("replied to {} for {}wp, {}. Article was not found.".format(
                username, langcode, articlename))
    
    def rgb(self, tweet):
        r,g,b = tweet['text'].split()[1:4]
        username = tweet['user']['screen_name']
        samplefile = make_rgb_sample(r,g,b)
        # update with image
        with open(samplefile, 'rb') as sample:
            t.update_status_with_media(
                status = "@{}".format(username),
                in_reply_to_status_id = tweet['id'],
                media = sample
            )
        
    
    def bf(self, tweet):
        text = tweet['text']
        username = tweet['user']['screen_name']
        
        code = text[text.find(' ')+1:]
        code = HTMLParser().unescape(code)
        mybf = bf.BrainSth(50)
        mybf.give_code(code)
        exec_val = mybf.execute()
        
        self.t.update_status(status = "@{} {}".format(username, exec_val),
                               in_reply_to_status_id = tweet['id'])
        print("executed bf command {} from @{}, returned {}.".format(
            code, username, exec_val))
    
    def randc(self, tweet):
        text = tweet['text']
        body = text[text.index(' ')+1:]
        choices = list(map(lambda x: x.strip(), body[body.index(' ')+1:].split(',')))
        username = tweet['user']['screen_name']
        selected = HTMLParser().unescape(random.choice(choices))
        
        self.t.update_status(status = "@{} {}".format(username, selected),
                               in_reply_to_status_id = tweet['id'])
        print("asked choice from {} by @{}. Returned {}.".format(
            choices, username, selected))
    
    def ping(self, tweet):
        username = tweet['user']['screen_name']
        self.t.update_status(status = "@{} I'm online".format(username),
                               in_reply_to_status_id = tweet['id'])
        print("pinged by @{}.".format(username))
    
    def weather(self, tweet):
        text = tweet['text']
        username = tweet['user']['screen_name']
        cities = text.split()[2:]
        frcs = ''
        for city in cities:
            try:
                frcs += weather.WForecast(city).forecast()
            except ValueError:
                frcs += 'city {} not found\n'.format(city)
        
        limit = 140 - 1 - len(username) - 1
        if frcs[-1] == '\n':
            frcs = frcs[:-1]
        if len(frcs) > limit:
            frcs = frcs[:limit-3]+"文字数"
        
        self.t.update_status(status = "@{} {}".format(username, frcs),
                            in_reply_to_status_id = tweet['id'])
        print("asked for weather in {} by @{}".format(
            cities, username))

def main():
    butlr = Butlr()
    butlr.update()


if __name__ == '__main__':
    main()
