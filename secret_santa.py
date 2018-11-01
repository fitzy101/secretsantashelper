import os
import getopt
import sys
import hashlib
import json
import textwrap
import random
from twilio.rest import Client

def usage():
    print (textwrap.dedent(("""{} --config-file=<path-to-json-file> [--dry-run --dollar-limit=<limit(integer)> --message-service=<service> --twilio-sid=<sid> --twilio-api-key=<api_key> --from-num=<number>]

    --config-file       file path to the configuration file (required)
    --dry-run           print out the messages, and don't send anything
    --dollar-limit      change the dollar limit from the default of $50
    --message-service   the SMS message API to use; currently only supports twilio
    --from-num          the 'from' number for the message service

    Twilio Specific
    --twilio-sid        the twilio SID account number
    --twilio-api-key    your API key
    """.format(sys.argv[0]))))

def main():

    # parse all args
    arg_list = "dry-run dollar-limit= config-file= twilio-sid= twilio-api-key= message-service= from-num= help"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", arg_list.split())
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    dry_run = False
    config_file = None
    dollar_limit = 50 # default of $50
    twilio_sid = None
    twilio_api_key = None
    msg_service = None
    from_num = None
    if len(sys.argv) == 1:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == "--dry-run":
            dry_run = True
        elif o == "--dollar-limit":
            dollar_limit = a
        elif o == "--config-file":
            config_file = a
        elif o == "--message-service":
            msg_service = a
        elif o == "--twilio-sid":
            twilio_sid = a
        elif o == "--twilio-api-key":
            twilio_api_key = a
        elif o == "--from-num":
            from_num = a
        elif o == "--help":
            usage()
            sys.exit(1)
        else:
            usage()
            sys.exit(2)

    # validate args
    if config_file is None:
        print("no config file provided", file=sys.stderr)
        usage()
        sys.exit(2)

    if msg_service is None and not dry_run:
        print("no message service provided and not a dry run", file=sys.stderr)
        usage()
        sys.exit(2)

    if from_num is None and not dry_run:
        print("no 'from' number provided and not a dry run", file=sys.stderr)
        usage()
        sys.exit(2)

    if msg_service == "twilio" and not (twilio_sid or twilio_api_key):
        print("twilio requires sid and api_key", file=sys.stderr)
        usage()
        sys.exit(2)
    
    receivers = []
    with open(config_file, "r") as f:
        try:
            cfg = json.loads(f.read())
        except Exception as err:
            raise Exception(str(err))
        for p in cfg:
            receivers.append(
                    Receiver(p['full_name'], p['ph_number']))

    # determine send/receive list
    for receiver in receivers:
        receiver.person_given = find_random_giftee(receiver, receivers)

    # send the messages/print to out
    for receiver in receivers:
        msg = message(receiver, receiver.person_given, dollar_limit)
        if dry_run:
            print (msg)
        else:
            if msg_service == "twilio":
                send_twilio_message(receiver, msg, twilio_sid, twilio_api_key, from_num)
            else:
                print("message service not supported!", file=sys.stderr)
                sys.exit(1)


def find_random_giftee(from_p, receivers):
    # randomize a few times
    idx = None
    for i in range(10):
        idx = random.randint(0, len(receivers)-1)
    while receivers[idx].chosen or receivers[idx].id == from_p.id:
        idx = random.randint(0, len(receivers)-1)
    receivers[idx].chosen = True
    return receivers[idx]

def message(from_p, to_p, limit):
    return textwrap.dedent("""
        HoHoHo {}, you have received your Secret Santa giftee!
        You will be finding a gift for {} with a limit of ${}. Christmas is
        right around the corner, so get creative!
        """).format(from_p.full_name, to_p.full_name, limit)

def send_twilio_message(from_p, msg, sid, api_key, from_num):
    """ send with twilio api """
    client = Client(sid, api_key)
    message = client.messages.create(
        from_=from_num,
        body=msg,
        to=from_p.ph_number
    )
    print("successfully sent message to {} {}: {}".format(from_p.ph_number, from_p.full_name, message.sid))
    return

class Receiver:
    def __init__(self, full_name, ph_number):
        self._full_name = full_name
        self._ph_number = ph_number
        self._person_given = None
        self._chosen = False

        # The unique identifier for this recipient based on their full_name and phone
        # number.
        self._id = hashlib.sha1(str.encode("{}{}".format(
            self.full_name, self.ph_number))).hexdigest()
        return
    
    @property
    def full_name(self):
        return self._full_name

    @property
    def ph_number(self):
        return self._ph_number

    @property
    def person_given(self):
        return self._person_given

    @person_given.setter
    def person_given(self, value):
        self._person_given = value
        return

    @property
    def chosen(self):
        return self._chosen

    @chosen.setter
    def chosen(self, value):
        self._chosen = value
        return

    @property
    def id(self):
        return self._id
    
if __name__ == "__main__":
    main()

