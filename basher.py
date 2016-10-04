#!/usr/bin/env python
from flow import Flow
import os
import random
import string
from IPython import embed
import time
from subprocess import Popen, PIPE


"""
the permission model is like this: any account can request to join an
organization, but it has to know the org ID.  From there, accounts must be
invited to channels within the org.
"""


def get_or_create_account(bot):
    """Check if account is installed."""
    flow = Flow()

    print("* Checking if account is already installed...")
    try:
        flow.start_up(
            username=bot['username'],
        )
        print("* Account already installed.")
    except Flow.FlowError as e:
        print(e)
        print("* Account not installed, trying local device creation...")
        try:
            flow.create_device(username=bot['username'],
                               password=bot['password']
                               )
            time.sleep(2)
            print("* Account has been installed locally.")
        except Flow.FlowError as e:
            print(e)
            print("* Account does not exist, creating account...")

            try:
                flow.create_account(*bot)
            except Exception as e:
                print(e)

    flow = Flow(bot["username"])
    return flow

bot = {}
bot["username"] = os.environ.get("SEMAPHOR_BASHER_USERNAME")
bot["password"] = os.environ.get("SEMAPHOR_BASHER_PASSWORD")
bot["phone_number"] = "".join(random.choice(string.digits) for _ in range(10))
bot["device_name"] = "leetlebox"

team = {}
team["name"] = "SparklePalace"
team["invite_code"] = os.environ.get("SEMAPHOR_SPARKLEPALACE_INVITE_CODE")

flow = get_or_create_account(bot)
orgs = flow.enumerate_orgs()

for org in orgs:
    channels = flow.enumerate_channels(org['id'])
    for channel in channels:
        msg = flow.send_message(org['id'], channel['id'], "It's me, basher!")


def exec_cmd(cmd):
    print("received command: {}".format(cmd))
    cmd = cmd.split()
    ret = {}
    try:
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"input data; passed to subprocess' stdin")
        rc = p.returncode
        ret['output'] = output
        ret['err'] = err
        ret['rc'] = rc
    except OSError as e:
        print(e)
        ret['err'] = e
    except Exception as e:
        print(e)
        embed()
    return ret


@flow.message
def check_message(notif_type, data):
    regular_messages = data["regularMessages"]
    for message in regular_messages:
        msg = message["text"]
        cid = message["channelId"]
        channel = flow.get_channel(cid)
        oid = channel["orgId"]

        # Parse the message
        if not is_it_for_me(flow.account_id(), is_dm(channel), message):
            continue
        cmd = msg
        result = exec_cmd(cmd)
        for k in result:
            if result[k]:
                flow.send_message(oid, cid, "{}: \r{}".format(k, result[k]))


def is_dm(channel):
    return channel['purpose'] == u'direct message'


def is_it_for_me(account_id, dm, message):
    # If it's my message, ignore it
    if message["senderAccountId"] == account_id:
        return False
    # If it's a direct message, then we care about it
    if dm:
        return True
    # Am I highlighted?
    other_data = message['otherData']
    if len(other_data) > 0:
        # dirty way ot figure out if we are being highlighted
        if account_id.lower() in other_data.lower():
            return True
    return False

if __name__ == "__main__":
    # Main loop to process notifications.
    print("Listening for incoming messages... (press Ctrl-C to stop)")
    flow.process_notifications()
