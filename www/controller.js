$(document).ready(function () {
    // Display Speak Message
    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        $(".siri-messages li:first").text(message);
        $('.siri-messages').textillate('start');
    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    eel.expose(ShowSiri)
    function ShowSiri() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
    }
});