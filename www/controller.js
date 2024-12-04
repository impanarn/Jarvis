$(document).ready(function () {
    
    // Display Speak Message
    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        $(".siri-messages li:first").text(message);
        $('.siri-messages').textillate('start');
    }
});

