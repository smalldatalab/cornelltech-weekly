#!/usr/bin/env python

from private_config import SLACK_TOKEN
from slackclient import SlackClient
from digestlib import *

# some initial settings
TARGET_ADDRESS = 'falquaddoomi@gmail.com'
included_channels = [u'building_comments', u'cafe_comments']

# --- preamble: connect to slack w/private token
sc = SlackClient(SLACK_TOKEN)


# ---
# --- step 1. acquire channel/user/emoji metadata
# ---

# acquire channel metadata
channel_info = sc.api_call("channels.list")
channels = channel_info['channels']

# acquire users mapping
users = sc.api_call("users.list")
users_map = dict([(x['id'], x['name']) for x in users['members']])

# create channel-to-id mapping for channels of interest
channel_ids = dict([(k['name'], k['id']) for k in channels if k['name'] in included_channels])


# ---
# --- step 2. get actual channel messages
# ---

channel_comments = {}

for cid in channel_ids:
    print "grabbing history for %s..." % cid
    # grab the history for each
    results = sc.api_call("channels.history", channel=channel_ids[cid], count=1000)
    channel_comments[cid] = results['messages']
    
# this transformed version is used elsewhere
chat_messages = [
    msg for msg in reversed(channel_comments['cafe_comments'])
    if msg['type'] == 'message' and 'subtype' not in msg and 'thread_ts' not in msg
]


# ---
# --- step 3. format and create messages
# ---

from IPython.display import display, Markdown, HTML
from itertools import groupby
import re


find_names_re = re.compile(r'<@([^>]+)>')
find_emoji_re = re.compile(r':(?P<sn>[^:]+):(:(?P<mod>[^:]+):)?')


def replace_name_html(m):
    try:
        return '<b style="color: #3393cc;">@%s</b>' % users_map[m.group(1)]
    except KeyError:
        return "<b>%s</b>" % m.group(0)
    
    
def replace_emoji(m):
    try:
        emoji = shortname_to_emoji[m.group('sn')]
        
        if m.group('mod') and 'skin_variations' in emoji:
            # just print the emoji + variation out as two separate characters
            mod = shortname_to_emoji[m.group('mod')]
            # variation = emoji['skin_variations'][mod['unified']]
            return "&#x%s;&#x%s;" % (emoji['unified'], mod['unified'])
        else:
            return "&#x%s;" % emoji['unified']
    except KeyError:
        return m.group(0)

    
# compute time bounds
start_time = min(min(float(msg['ts']) for msg in messages) for messages in channel_comments.values())
end_time = max(max(float(msg['ts']) for msg in messages) for messages in channel_comments.values())

start_datetime, end_datetime = localize_ts(start_time), localize_ts(end_time)
start_datestr, end_datestr = custom_strftime("%A, %B {S}, %Y", start_datetime), custom_strftime("%A, %B {S}, %Y", end_datetime)

print "%s to %s" % (start_datestr, end_datestr)


# gathers output for emission
emissions = []
def emit(mkdown):
    global emissions
    emissions.append(mkdown)

    
emit(HTML("""<div style="text-align: center; margin-bottom: 2em;">
<h1 style="margin-bottom: 0.5em; font-size: xx-large;">Cornell Tech Weekly Digest</h1>
<div style="font-size: large; line-height: 150%%; color: #777;">messages from %(channel_list)s<br />from %(start_datestr)s to %(end_datestr)s</div>
</div>""" % {
    'channel_list': ", ".join([('<b style="color: black;">#%s</b>' % name) for name in channel_comments]),
    'start_datestr': '<b style="color: black;">%s</b>' % start_datestr,
    'end_datestr': '<b style="color: black;">%s</b>' % end_datestr
}))

# actually iterate over the messages now
for channel_name, comments in channel_comments.items():
    personal_messages = [
        msg for msg in reversed(comments)
        # if msg['type'] == 'message' and 'subtype' not in msg
        if msg['type'] == 'message' and 'subtype' not in msg and 'thread_ts' not in msg
    ]
    localized_chats = [
        {
            'datetime': (datetime
            .fromtimestamp(float(msg['ts']), timezone('UTC'))
            .astimezone(timezone('US/Eastern'))),
            'text': msg['text'],
            'user': msg['user']
        }
        for msg in personal_messages
    ]
    
    # actually print stuff now
    
    emit(HTML('<div style="margin-left: auto; padding: 20px; padding-top: 10px; margin-right: auto; margin-bottom: 1em; max-width: 600px; border-radius: 3px; border: solid 1px #ccc;">'))
    
    emit(HTML('<h2 style="font-size: x-large;">#%s</h2><hr color="#ccc" size="1" style="color: #ccc;" />' % channel_name))

    for day, messages in groupby(localized_chats, lambda x: custom_strftime("%A, %B {S}", x['datetime'])):
        emit(HTML('<h3 style="color: #555;">%s</h3>' % day))
        emit(HTML('<ul style="margin-bottom: 0.5em;">'))
        
        for message in messages:
            final_text = find_names_re.sub(replace_name_html, message['text'])
            final_text = find_emoji_re.sub(replace_emoji, final_text)
            
            data = {
                'text': final_text,
                'timeofday': custom_strftime("%-I:%M %p", message['datetime']),
                'author': users_map[message['user']]
            }
            emit(HTML("""<li style="margin-bottom: 0.5em;"><b style="font-size: larger;">%(author)s</b> <span style="color: #777; font-size: smaller;">%(timeofday)s</span><br />%(text)s</li>""" % data))
        
        emit(HTML("</ul>"))
        
    emit(HTML("</div>"))


# ---
# --- step 4. send email to target address
# ---

import yagmail
yag = yagmail.SMTP('falquaddoomi')

from markdown import markdown
html = ""

for em in emissions:
    if type(em) == Markdown:
        html += markdown(em.data, safe_mode='escape')
    else:
        html += em.data

# html = "".join([markdown(x.data, safe_mode='escape') for x in emissions])
html = find_emoji_re.sub(replace_emoji, html)

print "Sending mail to %s..." % TARGET_ADDRESS
print yag.send(TARGET_ADDRESS, 'Cornell Tech Weekly Digest (rev2)', html)
