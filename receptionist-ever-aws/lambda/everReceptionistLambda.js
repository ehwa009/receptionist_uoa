'use strict';

var directions = require('directions');

 /**
  * This sample demonstrates an implementation of the Lex Code Hook Interface
  * in order to serve a sample bot which manages reservations for hotel rooms and car rentals.
  * Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
  * as part of the 'BookTrip' template.
  *
  * For instructions on how to set up and test this bot, as well as additional samples,
  *  visit the Lex Getting Started documentation.
  */


 /** --------------------------------------------------------------------------------------
  * --------------- Helpers that build all of the responses ------------------------------
  * --------------------------------------------------------------------------------------
  */
function elicitSlot(sessionAttributes, intentName, slots, slotToElicit, message) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'ElicitSlot',
            intentName,
            slots,
            slotToElicit,
            message
        },
    };
}

function elicitIntent(sessionAttributes, message) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'ElicitIntent',
            message: message
        },
    };
}

function confirmIntent(sessionAttributes, intentName, slots, message, responseCard) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'ConfirmIntent',
            intentName,
            slots,
            message,
            responseCard
        }
    };
}

function close(sessionAttributes, fulfillmentState, message, responseCard) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'Close',
            fulfillmentState,
            message,
            responseCard
        }
    };
}

function delegate(sessionAttributes, slots) {
    return {
        sessionAttributes,
        dialogAction: {
            type: 'Delegate',
            slots,
        },
    };
}
 /** --------------------------------------------------------------------------------------
  * ---------------------------------------------------------------------------------------
  */


function getGoodByeMessage() {
    return {
        contentType : "PlainText",
        content: "Ok, enjoy your visit to the Newmarket campus."
    };
}

function getDirectionsMessage() {
    return {
        contentType : "PlainText",
        content: "Do you know how to get there?"
    };
}

function getRequestNameMessage(personVisiting) {
    return {
        contentType : "PlainText",
        content : "Ok I will email " + personVisiting + " about your arrival. Could I please get your name?"
    };
}

function getFurtherHelpMessage() {
    return {
        contentType : "PlainText",
        content : "Is there anything else I can help you with?"
    };
}

function welcome(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};

    var welcomeMsg = {
        contentType: 'PlainText',
        content : 'Hi, I\'m Ever Robot Receptionist. Welcome to the Newmarket Campus. How can I help you?'
    }

    callback(elicitIntent(sessionAttributes, welcomeMsg));
    return;
}

function thankYou(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};

    var thankYouMsg = {
        contentType : "PlainText",
        content: "You're welcome. Please feel free to let me know if you require further assistance."
    };

    callback(elicitIntent(sessionAttributes, thankYouMsg));
    return;
}

function checkAppointment(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};
    const slots = intentRequest.currentIntent.slots;
    
    var appointmentMsg = {
        contentType: 'PlainText',
        content : '[error]Sure, do you have an appointment with ' + slots.Person
    }
    sessionAttributes.personVisiting = slots.Person;
    
    if (intentRequest.currentIntent.confirmationStatus === 'Denied') {
        callback(confirmIntent(sessionAttributes, "EverGetName", {}, null));
    }
    else {
        callback(elicitIntent(sessionAttributes, appointmentMsg));
    }





    // This make a flow between user and bot
    //callback(confirmIntent(sessionAttributes, "EverAskIfKnowDirections", {}, appointmentMsg, null));
    return;
}

function askIfKnowDirections(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};
    const slots = intentRequest.currentIntent.slots;

    var errMsg = {
        contentType: 'PlainText',
        content: 'Sorry didn\'t understand your response. Do you have an appointment?'
    }

    var getNameMsg = {
        contentType : "PlainText",
        content : "Ok I will email " + sessionAttributes.personVisiting + " about your arrival. Could I please get your name?"
    }

    if (intentRequest.currentIntent.confirmationStatus === 'Denied') {
        //callback(elicitSlot(sessionAttributes, "EverGetName", {"Name": "", "Place": ""}, "Name",  getRequestNameMessage(sessionAttributes.personVisiting)));
        callback(confirmIntent(sessionAttributes, "EverGetName", {"Name": "", "Place": ""}, getNameMsg, null));
    } 
    else if (intentRequest.currentIntent.confirmationStatus === 'Confirmed') {
        callback(confirmIntent(sessionAttributes, 'EverSayDirections', {}, getDirectionsMessage()));
    } 
    else {
        callback(confirmIntent(sessionAttributes, 'EverAskIfKnowDirections', {}, errMsg))
    }
}

function sayDirections(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};
    const slots = intentRequest.currentIntent.slots;

    var errMsg = {
        contentType: 'PlainText',
        content: 'Sorry didn\'t understand your response. Do you know how to get there?'
    }

    if (intentRequest.currentIntent.confirmationStatus === 'Denied') {
        callback(elicitIntent(sessionAttributes, directions.getDirections(sessionAttributes.personVisiting)));
    } else if (intentRequest.currentIntent.confirmationStatus === 'Confirmed') {
        callback(elicitIntent(sessionAttributes, getGoodByeMessage()));
    } else {
        callback(confirmIntent(sessionAttributes, 'EverSayDirections', {}, errMsg))
    }
}

function sendEmail(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};
    const slots = intentRequest.currentIntent.slots;
    
    var emailMsg = {
        contentType: 'PlainText',
        content : 'Thanks, please take a seat. ' + sessionAttributes.personVisiting + ' has been notified of your arrival.'
    }

    callback(elicitIntent(sessionAttributes, emailMsg));
    return;
}


function goodbye(intentRequest, callback) {
    const sessionAttributes = intentRequest.sessionAttributes || {};
    const slots = intentRequest.currentIntent.slots;

    callback(close({}, 'Fulfilled', getGoodByeMessage()))
}

// --------------- Intents -----------------------

/**
 * Called when the user specifies an intent for this skill.
 */
function dispatch(intentRequest, callback) {
    // console.log(JSON.stringify(intentRequest, null, 2));
    console.log(`dispatch userId=${intentRequest.userId}, intentName=${intentRequest.currentIntent.name}`);
    console.log(intentRequest);

    const intentName = intentRequest.currentIntent.name;

    // Dispatch to your skill's intent handlers
    if (intentName === 'EverWelcome') {
        return welcome(intentRequest, callback);
    } else if (intentName == 'Meeting') {
        return checkAppointment(intentRequest, callback);
    } else if (intentName == 'EverAskIfKnowDirections') {
        return askIfKnowDirections(intentRequest, callback);
    } else if (intentName == 'EverGetName') {
        return sendEmail(intentRequest, callback);
    } else if (intentName == 'EverSayDirections') {
        return sayDirections(intentRequest, callback);
    } else if (intentName == 'EverThankYou') {
        return thankYou(intentRequest, callback);
    }/*else if (intentName == 'EverLocation') {
        return continueFinding(intentRequest, callback);
    } else if (intentName == 'EverAskIfKnowDirections') {
        return goodbye(intentRequest, callback);
    } else if (intentName == 'UnsureResult') {
        return unsureResult(intentRequest, callback);
    }*/

    throw new Error(`Intent with name ${intentName} not supported`);
}

// --------------- Main handler -----------------------

function loggingCallback(response, originalCallback) {
    console.log(JSON.stringify(response, null, 2));
    originalCallback(null, response);
}

// Route the incoming request based on intent.
// The JSON body of the request is provided in the event slot.
exports.handler = (event, context, callback) => {
    try {
        // preprocess
        console.log(`event.bot.name=${event.bot.name}`);
        dispatch(event, (response) => loggingCallback(response, callback));
    } catch (err) {
        callback(err);
    }
};
