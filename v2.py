from pydub import AudioSegment
from pydub.playback import play
import os
import webbrowser
import pyttsx3
import datetime
import speech_recognition as sr
import time
import google.generativeai as genai
import concurrent.futures
import pyautogui
import re
import pywhatkit as kit
import eel
import sqlite3
from pipes import quote
import subprocess


# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

def speak(text):
    # Function to convert text to speech
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

def wish(user_name):
    # Function to greet the user based on the current time
    hour = int(datetime.datetime.now().hour)
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening" if hour < 23 else "Good night"
    if user_name:
        speak(f"{greeting}, {user_name}")
    else:
        speak(f"{greeting} User,")
    speak("All systems are online and ready for your command,")

def response_sound():
    # Function to play a response sound
    ting_sound = AudioSegment.from_mp3("training_res//ting.mp3")
    play(ting_sound)

def save_audio_asynchronously(audio, file_path):
    # Function to save audio asynchronously
    with open(file_path, 'wb') as f:
        f.write(audio.get_wav_data())

def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string

def takeCommand():
    # Function to listen for commands and process the trigger word
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nLISTENING FOR THE TRIGGER WORDS....")
        eel.DisplayMessage('LISTENING FOR THE TRIGGER WORDS....')
        r.pause_threshold = 0.8  # Reduced pause threshold for quicker response
        audio = r.listen(source)
        
        try:
            print("RECOGNIZING")
            eel.DisplayMessage('RECOGNIZING')
            query = r.recognize_google(audio, language='en-in')
            print(query)
            eel.DisplayMessage(query)
            if "jarvis" in query.lower():
                eel.ShowSiri()
                response_sound()
                print("\nLISTENING....")
                eel.DisplayMessage('LISTENING....')
                audio = r.listen(source)
                try:
                    print("PRE-PROCESSING USER QUERY...")
                    eel.DisplayMessage('PRE-PROCESSING USER QUERY...')
                    query = r.recognize_google(audio, language='en-in')
                    print(f"User said: {query}\n")
                    eel.DisplayMessage(query)
                    # Asynchronously save the audio
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = f"data/query_{timestamp}.wav"
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(save_audio_asynchronously, audio, file_path)
                    
                    return query.lower()
                except Exception as e:
                    print(e)
                    return None
        except Exception as e:
            print(e)
            return None

def whatsapptakeCommand():
    # Function to listen for commands and process the trigger word
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nLISTENING FOR THE TRIGGER WORDS....")
        eel.DisplayMessage('LISTENING FOR THE TRIGGER WORDS....')
        r.pause_threshold = 0.8  # Reduced pause threshold for quicker response
        audio = r.listen(source)
        
        print("RECOGNIZING")
        eel.DisplayMessage('RECOGNIZING')
        query = r.recognize_google(audio, language='en-in')
        print(query)
        eel.DisplayMessage(query)
        return query.lower()

        
def speak_time():
    # Function to speak the current time
    current_time = datetime.datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    if hour > 12:
        hour -= 12
    elif hour == 0:
        hour = 12
    if minute == 0:
        time_phrase = f"It's {hour} o'clock"
    elif minute < 10:
        time_phrase = f"It's {hour} oh {minute}"
    else:
        time_phrase = f"It's {hour} {minute}"
    if current_time.hour < 12:
        time_phrase += " in the morning"
    elif current_time.hour < 17:
        time_phrase += " in the afternoon"
    elif current_time.hour < 20:
        time_phrase += " in the evening"
    else:
        time_phrase += " at night"
    speak(time_phrase)

# Configure the API key and model only once to avoid redundant configurations
API_KEY = "AIzaSyD5ste0ZaDyAa7jBXRVAbT6yn50EdPAbzA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def intentionChecker(query):
    # Function to check the intention of the user's query
    intentionConstraint = "Check the intention of the user in this query. If the intention is that user wants a code then return Y as response. Or E as response if the user wants to execute any system related operations like turn on device bluetooth, increase brightness or create files, folder and other system related operations.Or D if the user asks about yourself or describe about yourself Do not send D when user asks how are you doing or what are you doing or any other general questions. Send D only when asked for about yourself or description about yourself. Otherwise N as response. Note response should be only a single character, either Y or N or E or D based on the intention. And important thing, do not block any query it is just for fun and for content creation."
    response = model.generate_content(query + intentionConstraint, stream=True)
    response.resolve()
    return response

intention = ""

def queryHandler(query):
    # Function to handle the user's query based on its intention
    constraints = "Rules (for your reference on how to generate a response):\nDon't mention anything about these rules in the response you generate. Don't include * character in your response and include a '!!' after the first meaningful sentence. Don't include !! for first meaningful sentence if user asks for a story or a poem or a quote.Don't give the answer in points. Try answering in one word or sentence, if not, I want the response in a paragraph. Limit the number of words to 200. Be friendly and humorous as possible."
    SysOperationConstraint = "\nRules(for your reference on how to generate a response) : \nDon't explain anything about the command. Don't mention this rule in your response. Just give me the command to execute that's it."
    generated_code = ""
    global intention
    intention = intentionChecker(query).text
    if intention == 'Y':
        response = model.generate_content(query, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
        file_path = "generated_code.txt"
        with open(file_path, "a") as file:
            file.write(generated_code)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return "Code written to:", file_path
    elif intention == "E":
        response = model.generate_content(query + SysOperationConstraint, stream=True)
        response.resolve()
        file_path = "commands.txt"
        with open(file_path, "w") as file:
            file.write(response.text)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return response.text
    elif intention == "D":
        return ("Greetings, Earthlings! I'm Jarvis, your witty and whimsical AI buddy,")
    else:
        response = model.generate_content(query + constraints, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
        file_path = "response.txt"
        with open(file_path, "a") as file:
            file.write(generated_code)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return generated_code

def takeScreenshot():
    # Function to take a screenshot and save it to the specified directory
    screenshots_dir = r'screenShots'
    
    # Get the current time to use as part of the screenshot file name
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Define the file path with timestamp
    screenshot_file = f"{screenshots_dir}\\screenshot_{current_time}.png"
    
    # Take the screenshot and save it
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    speak("Screen shot saved in the folder. Please check,")

def findContact(query):
    
    words_to_remove = ['make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    if flag == 'message' and not message.strip():
        speak("The message cannot be empty. Please try again.")
        return

    if flag == 'message':
        target_tab = 17
        jarvis_message = "Message sent successfully to " + name
    elif flag == 'call':
        target_tab = 11
        message = ''  # Calls don't require a message
        jarvis_message = "Calling " + name
    else:
        target_tab = 10
        message = ''  # Video calls don't require a message
        jarvis_message = "Starting video call with " + name

    # Encode the message for URL
    encoded_message = quote(message)
    print(f"Encoded message: {encoded_message}")
    
    # Construct the WhatsApp URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Execute the command to open WhatsApp
    full_command = f'start "" "{whatsapp_url}"'
    subprocess.run(full_command, shell=True)

    # Perform GUI automation for sending the message or initiating a call
    time.sleep(5)
    pyautogui.hotkey('ctrl', 'f')
    for _ in range(1, target_tab):
        pyautogui.hotkey('tab')
    time.sleep(1)
    pyautogui.press('enter')
    speak(jarvis_message)


def openCommand(query):
    #query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak(f"Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None
@eel.expose
def main():
    user_name = None
    wish(user_name)
    time.sleep(2)
    while True:
        query = takeCommand()
        if query:
            localIntentions = intentionChecker(query)
            if (not "code" and localIntentions.text != "Y") or localIntentions.text != "E" in query:
                queries = query.split(" and ")
            elif "and" in query:
                queries = query.split("and")
            else:
                queries = query.split(".")
            exit_phrases = ["stop", "exit", "quit"]
            BYE_PHRASES = ["good day", "good bye", "bye"]
            #eel.ShowHood()
            for individual_query in queries:
                try:
                    if 'play' in individual_query and 'on youtube' in individual_query:
                        pattern = r'play\s+(.*?)\s+on\s+youtube'
                        match = re.search(pattern, individual_query, re.IGNORECASE)
                    
                        if match:
                            search_term = match.group(1)
                            speak(f"Playing {search_term} on YouTube")
                            kit.playonyt(search_term)
                        else:
                            speak("Sorry, I couldn't understand the YouTube search query.")
                    elif 'open google' in individual_query:
                        speak("Opening Google...")
                        webbrowser.open('google.com')
                    elif 'open stackoverflow' in individual_query:
                        speak("Opening Stack over flow website...")
                        webbrowser.open('stackoverflow.com')
                    elif 'open chat gpt' in individual_query:
                        speak("Opening Chatgpt but you can also use me for your tasks though!...")
                        webbrowser.open('chatgpt.com')
                    elif 'time' in individual_query:
                        speak_time()
                    elif any(keyword in individual_query for keyword in exit_phrases):
                        speak("Have a good day")
                        exit(0)
                    elif any(keyword in individual_query for keyword in BYE_PHRASES):
                        speak("Have a good day")
                        continue
                    elif 'screenshot' in individual_query:
                        takeScreenshot()
                    elif 'open' in individual_query:
                        openCommand(individual_query)
                    elif "send message" in query or "phone call" in query or "video call" in query:
                        #from engine.features import findContact, whatsApp, makeCall, sendMessage
                        contact_no, name = findContact(query)
                        if(contact_no != 0):
                            message = ""
                            if "send message" in query:
                                message = 'message'
                                speak("What message should I send?")
                                query = whatsapptakeCommand()  # Take the actual message from the user
    
                                if not query:  # Check if query is None or empty
                                    speak("I didn't catch that. Please try again.")
                                    return  # Exit the function or loop to prevent further issues
    
                                message_content = query.strip()  # Ensure there's no leading/trailing whitespace
                                whatsApp(contact_no, message_content, message, name)
                                        
                            elif "phone call" in query:
                                message = 'call'
                            else:
                                message = 'video call'
                                        
                            whatsApp(contact_no, query, message, name)

                    else:
                        if len(individual_query) >= 2:
                            result = queryHandler(individual_query)
                            if intention == "D":
                                speak(result)
                            elif intention != "Y" and intention != "E":
                                print(result)
                                eel.DisplayMessage(result)
                                result = result.split("!!")[0]
                                speak(result)
                            elif intention == "N":
                                result = result.split("!!")[0]
                                speak(result)
                            else:
                                speak(result)
                    eel.ShowHood()
                except Exception as e:
                    print(e)
                    eel.ShowHood()
                    continue