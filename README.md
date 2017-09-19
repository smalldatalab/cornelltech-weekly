# cornelltech-weekly

Scripts to produce a weekly email digest from posts to cornell tech's #building_comments and #cafe_comments channels

# Installation

After cloning the repository, run the following commands in the checked-out folder:

`virtualenv .venv && source .venv/bin/activate && pip install -r requirements`
`npm install`

You must create a file called `private_config.py` and add the following line to it:

`SLACK_TOKEN = "<your web token here>"`

This script uses Slack's legacy tokens; you can obtain a token for your organization here:
https://api.slack.com/custom-integrations/legacy-tokens

# Usage

Edit the variables at the top of `send_digest.py`, specifically `TARGET_ADDRESS` and `included_channels`.

Run the script by executing `python send_digest.py`, which will send a digest summary email to `TARGET_ADDRESS`. Note that you should run the script interactively the first time, as you'll be prompted for a password for the gmail account. Save the password if you wish future runs to be executable non-interactively (e.g. as a cron job).
