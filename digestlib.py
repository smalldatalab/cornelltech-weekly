import json
from datetime import datetime
from pytz import timezone

# build emoji mapping
with open("./node_modules/emoji-datasource-apple/emoji.json") as fp:
    emoji = json.load(fp)
    shortname_to_emoji = dict([(x['short_name'], x) for x in emoji])

    
# nice date formatting
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def localize_ts(ts, tzone='US/Eastern'):
    return (datetime
            .fromtimestamp(float(ts), timezone('UTC'))
            .astimezone(timezone(tzone)))


# markdown formatting
    
def escape_markdown(text):
    return text.replace("*", "\*")