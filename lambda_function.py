"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests, re


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the UCSC Bus Bot. " \
                    "Please state the bus stop id or location to get started "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your bus stop by saying, " \
                    "Bus Stop Bay and Meder"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the UCSC Bus Bot. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know the bus stop you are in is  " + \
                        favorite_color + \
                        ". You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
        reprompt_text = "You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
    else:
        speech_output = "I'm not sure what bus stop you are in. " \
                        "Please try again."
        reprompt_text = "I'm not sure what bus stop you are in " \
                        "You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def set_bustop_from_session(intent, session):
    if 'getbuss' in intent:
        
        favorite_color = intent['slots']['getbuss']['value']
        #session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know the bus stop you are in is  " \
                        ". You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
        reprompt_text = "You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
    else:
        speech_output = "I'm not sure what bus stop you are in. " \
                        "Please try again."
        reprompt_text = "I'm not sure what bus stop you are in " \
                        "You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
    return build_response({}, build_speechlet_response(
        "none", speech_output, reprompt_text, False))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def get_stop_info_url(stop):
    return "https://www.scmtd.com/en/routes/schedule-by-stop/" + str(stop)

def get_next_buss_by_id(id):
    url = get_stop_info_url(id)
    r = requests.get(url)
    website = r.text
    times = re.findall("(\d+)</a></th><td>(\d+):(\d+)(\w+)<\/td>", website)
    first_element = times[0]
    next_buss = first_element[0]
    next_hour = first_element[1]
    next_minute = first_element[2]
    next_daytime = first_element[3]
    successful = True
    if(successful):
        speech_output = "The next bus is a " + str(next_buss) + " at " + str(next_hour) + " " + \
                        str(next_minute) + " " + next_daytime
        reprompt_text = "The next bus is a " + str(next_buss) + " at " + str(next_hour) + " " + \
                        str(next_minute) + " " + next_daytime
    else:
        speech_output = "I'm not sure what bus stop you are in. " \
                            "Please try again."
        reprompt_text = "I'm not sure what bus stop you are in " \
                        "You can ask me where your bus stop is by asking, " \
                        "what bus stop am I on?"
    return build_response({}, build_speechlet_response(
        "none", speech_output, reprompt_text, False))


def get_stop_info_by_id(intent):
    if 'getbuss' in intent:
        buss_stop_id = intent['slots']['getStopID']['value']
        return get_next_buss_by_id(buss_stop_id)
    else:
        raise ValueError("Invalid indent")
    

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "getStopID":
        return get_stop_info_by_id(intent)
    elif intent_name == "getStopByName":
        return set_bustop_from_session(intent, session)
    if intent_name == "getstopcrown":
        return get_next_buss_by_id(1617)
    
    else:
        raise ValueError("Invalid indent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    #build_speechlet_response("title", "ree", "beee", False)
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
