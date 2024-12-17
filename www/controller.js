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
        $("#code").attr("hidden", true);
    }

    eel.expose(ShowSiri)
    function ShowSiri() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        $("#code").attr("hidden", true);
    }
    eel.expose(code);
    function code() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", true);
        $("#code").attr("hidden", false);
    }

    eel.expose(display_generated_code);
    function display_generated_code(code) {
        console.log("Generated Code:", code);
        document.getElementById("code-display").innerText = code; // Displaying the generated code in an element with id 'output'
  }

});