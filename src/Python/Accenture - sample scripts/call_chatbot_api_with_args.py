import requests

#module for system specific parameters and functions
import sys

#get all script arguments as a list, the index 0 argument is the script name
arguments_of_script = sys.argv
print(arguments_of_script)


#prints the first argument
AssignedTo = arguments_of_script[1]
CallerID  = arguments_of_script[2]
ReferenceID  = arguments_of_script[3]
RequestorID  = arguments_of_script[4]
TaskID = arguments_of_script[5]

print(TaskID)
#import HTTPBasicAuth
#logging.basicConfig(format='%(levelname)s %(message)s', level=logging.INFO)

# Chatbot endpoint to push new conversations
RELAY_URL = 'https://chatbot-a04850dirautobot.aiam-dh.com/api/v1/query'

# Authentication token of the relay
RELAY_TOKEN = 'rely_token'

# HTTP session object
session = requests.Session()

#Query
chatbotquery = "close michelin ticket id " + TaskID
print(chatbotquery)
# Chatbot REST resource to send to the conversation endpoint
# to : user we are sending the message to
# message : content sent
# contexts : to lock the user in a certain conversation context to be able
# to deal with the response. Here we set a rivescript topic, you could
# also set an dialogflow context.
RELAY_BODY = '''{{
  "contexts":[ {context}],
  "lang": "en",
  "query": ["{chatbotquery}"],
  "sessionId": "a510fe22-5f11-4f42-888d-32b9490217cb"
}}'''

# Contect, see dialogflow documentation for more information
RELAY_CONTEXT = '''{{
  "lifespan": 1,
  "name": "rivescript",
  "parameters": [
    {{
      "name": "username",
      "value": "{username}"
    }}
  ]
}}'''

# Message template
CHATBOT_MESSAGE = '''Hello, I'm the Michelin Automation bot.
I have been informed that there was a request to perform some automation script to correct an incident. 
to confirm please type in 'please automate job'
'''


def send_chatbot_message(username, servers, chatbotquery):
    ''' Sends one message to the chatbot about a user servers'''
    message = CHATBOT_MESSAGE.format(
        savings=1234, servers=456).replace('\n', '\\n')
    #logging.info('Sending to %s: %s' % (username, message))
    context = RELAY_CONTEXT.format(username=username)

    body = RELAY_BODY.format(username=username, message=message, 
                             context=context, chatbotquery=chatbotquery , subject='Unused servers to stop')
    tmpsessionid = 'a510fe22-5f11-4f42-888d-32b9490217cb'
    reqlang = 'en'
    print(body)
    req_args = {
        'verify': False,
        'stream': False,
        'timeout': 60.0,
        #	'lang' : reqlang,
        #	'sessionId' : tmpsessionid,
        'data': body,
        'headers': {
            'content-type': 'application/json',
            #     'Authorization': 'Bearer %s' % RELAY_TOKEN
        }
    }
    post_call = session.post(RELAY_URL, **req_args, auth=('admin', 'jfZTS7G7Anscx95d'))
    print(post_call)
    print(post_call.text)
    print(post_call.content)
    print(post_call.status_code)


# Request arguments
req_args = {
    'verify': False,
    'stream': False,
    'timeout': 60.0,
    # 'lang' : "en",
    # 'sessionId' : "a510fe22-5f11-4f42-888d-32b9490217cb",
    'data': "Hello World",
    'headers': {
        'content-type': 'application/json',
        #    'Authorization': 'Bearer %s' % RELAY_TOKEN
    }
}

# Post request
# session.post(RELAY_URL,**req_args)
send_chatbot_message("charles.grenet", "test", chatbotquery)
print("All good")