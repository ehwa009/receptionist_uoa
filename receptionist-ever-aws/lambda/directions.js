'use strict';

var locationsMap = {
    "wesley": "straight down the corridor, pass the offices, until you turn left into robotics lab",
    "sheng": "straight down the corridor, pass the offices, until you turn left into robotics lab",
    "eddie": "straight down the corridor, pass the offices, until you turn left into robotics lab",
    "bruce": "straight down the corridor and in the ECE staff offices",
    "ho seok": "straight down the corridor and in the ECE staff offices",
    "catherine": "straight down the corridor and in the ECE staff offices",
    "mohan": "straight down the corridor and in the ECE staff offices",
    "nasser": "straight down the corridor and in the ECE staff offices",
    "chris": "straight down the corridor, pass the offices, until you turn left into healthcare robotics lab",
    "soriya": "straight down the corridor, pass the offices, until you turn left into healthcare robotics lab",
    "fung": "straight down the corridor, beside the offices, on the left in the parallel computing lab",
}

var getDirections = function(personName) {
    var content = "";
    if (locationsMap[personName.toLowerCase()]) {
        content = 'You may find ' + personName + " " + locationsMap[personName.toLowerCase()];
    } else {
        content = "Sorry I'm not sure where to find " + personName + ". Please continue straight down the corridor for Electrical and Computer Engineering."
    }
    var directionsMsg = {
        contentType: 'PlainText',
        content: content
    }

    return directionsMsg;
}

module.exports = {
    getDirections : getDirections
}