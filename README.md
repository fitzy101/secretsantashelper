# secretsantashelper
Make deciding on Secret Santa a real secret!

secretsantas helper is a program that will randomize Secret Santa recipients, and send a text message to the person letting them know who they have received to purchase a gift.

To use the program, see the usage message:
```
$ python3 secret_santa.py
secret_santa.py --config-file=<path-to-json-file> [--dry-run --dollar-limit=<limit(integer)> --message-service=<service> --twilio-sid=<sid> --twilio-api-key=<api_key> --from-num=<number>]

    --config-file       file path to the configuration file (required)
    --dry-run           print out the messages, and don't send anything
    --dollar-limit      change the dollar limit from the default of $50
    --message-service   the SMS message API to use; currently only supports twilio
    --from-num          the 'from' number for the message service

    Twilio Specific
    --twilio-sid        the twilio SID account number
    --twilio-api-key    your API key
```


The list of people is configured via a json file, which is an array of objects containing a 'full_name' and 'ph_number' field.

```json
[
    {
        "full_name": "jessica bloggs",
        "ph_number": "04112112112112"
    },
    {
        "full_name": "jeoffrey bloggs",
        "ph_number": "04221221221221"
    }
]
```

Currently, only twilio can be used for the SMS service, however it is easy to write an adapter to work with any SMS API. Pull requests for new services welcome!


