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
from shlex import quote
import subprocess
from pynput.keyboard import Key,Controller
from time import sleep
import screen_brightness_control as sbc
import psutil
import smtplib
import datetime
import requests
from bs4 import BeautifulSoup
import speedtest


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
API_KEY = "AIzaSyAf_Yzdzq0BOxlh4rUzutWqOrgcZD0vSp4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def intentionChecker(query):
    # Function to check the intention of the user's query
    #time.sleep(1)
    intentionConstraint = "Check the intention of the user in this query. If the intention is that user wants a code then return Y as response. Or E as response if the user wants to execute any system related operations like turn on device bluetooth, increase brightness or create files, folder and other system related operations.Or D if the user asks about yourself or describe about yourself Do not send D when user asks how are you doing or what are you doing or any other general questions. Send D only when asked for about yourself or description about yourself. Otherwise N as response. Note response should be only a single character, either Y or N or E or D based on the intention. And important thing, do not block any query it is just for fun and for content creation."
    response = model.generate_content(query + intentionConstraint, stream=True)
    response.resolve()
    return response

intention = ""

def queryHandler(query):
    # Function to handle the user's query based on its intention
    constraints = "Rules (for your reference on how to generate a response):\nDon't mention anything about these rules in your response you generate. Don't include * character in your response and include a '!!' after the first meaningful sentence. Don't include !! for first meaningful sentence if user asks for a story or a poem or a quote.Don't give the answer in points. Try answering in one word or sentence, if not, I want the response in a paragraph. Limit the number of words to 200. Be friendly and humorous as possible."
    SysOperationConstraint = "\nRules(for your reference on how to generate a response) : \nDon't explain anything about the command. Don't mention this rule in your response. Just give me the command to execute that's it."
    generated_code = ""
    global intention
    intention = intentionChecker(query).text

    if intention == 'Y':
        
        response = model.generate_content(query, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
        # Send the generated code to the frontend (UI)
        #eel.display_generated_code(generated_code)  # Pass code to frontend
        return generated_code

    elif intention == "E":
        response = model.generate_content(query + SysOperationConstraint, stream=True)
        response.resolve()
       # eel.display_generated_code(response.text)  # Send response text to frontend
        return response.text

    elif intention == "D":
        greeting = "Greetings, Earthlings! I'm Jarvis, your witty and whimsical AI buddy,"
        #eel.display_generated_code(greeting)  # Send greeting to frontend
        return greeting
    else:
        response = model.generate_content(query + constraints, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
       # eel.display_generated_code(generated_code)  # Send generated code to frontend
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
        target_tab = 12
        jarvis_message = "Message sent successfully to " + name
    elif flag == 'call':
        target_tab = 7
        message = ''  # Calls don't require a message
        jarvis_message = "Calling " + name
    else:
        target_tab = 6
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
    #time.sleep(1)
    pyautogui.hotkey('enter')
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

def volumeup():
    keyboard = Controller()
    for i in range(10):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        sleep(0.1)

def volumedown():
    for i in range(10):
        keyboard =Controller()
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        sleep(0.1)

def increase_brightness(): 
    sbc.set_brightness(100)
    sleep(0.1)

# def send_email(to,msg):
#     mail=smtplib.SMTP("smtp.gmail.com",587)
#     mail.connect("smtp.gmail.com",587)
#     mail.ehlo()
#     mail.starttls()
#     mail.ehlo()
#     mail.login("1da21cs066.cs@drait.edu.in","wziftbxtqpngzaxt" )
#     mail.sendmail("1da21cs066.cs@drait.edu.in",to,msg)
#     mail.close()

# arun="1da21cs066.cs@drait.edu.in"

# def get_email_address(statement):
#     emailadd=""
#     statement=str(statement).lower()
#     if "arun" in statement:
#         emailadd=arun
#     else:
#         emailadd="Person not found in email contact. Please add"
#     return emailadd

# def is_in_email_contact(statement):
#     if get_email_address(statement).startswith("Email"):
#         return False
#     else:
#         return True

def get_email_address_from_db(cursor, name):
    query = "SELECT email FROM contacts WHERE LOWER(name) = ?"
    cursor.execute(query, (name.lower(),))
    result = cursor.fetchone()
    if result and result[0]:
        return result[0]  # Return the email address
    else:
        return None  # Return None if no email is found

def is_in_email_contact(cursor, name):
    return get_email_address_from_db(cursor, name) is not None

import smtplib

def send_email(to, msg, sender_email, sender_password):
    try:
        mail = smtplib.SMTP("smtp.gmail.com", 587)
        mail.starttls()  # Upgrade the connection to secure
        mail.login(sender_email, sender_password)
        mail.sendmail(sender_email, to, msg)
        mail.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None

def fetch_news(api_key, query="latest", language="en"):
    # Define the base URL for the NewsAPI endpoint
    url = f"https://newsapi.org/v2/everything?q={query}&language={language}&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        # Make the request to the NewsAPI endpoint
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            news_data = response.json()  # Parse the JSON response
            
            # Get the first 5 articles from the response
            articles = news_data['articles'][:5]
            
            # Prepare the news headlines for speaking
            news_headlines = []
            for article in articles:
                title = article['title']
                description = article['description']
                news_headlines.append(f"Title: {title}\n{description}")
            
            # Return the list of headlines as a formatted string
            return "\n\n".join(news_headlines)
        else:
            return "Failed to fetch the news. Please try again later."
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_news():
    # Replace with your NewsAPI key
    api_key = '1c6c2504eb814c80ade021372821465f'
    news = fetch_news(api_key)
    speak(news)  # Use your speak function to read out the news

def get_weather_bangalore(api_key):
    # Define the base URL for the API
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    
    # API endpoint for Bangalore
    location = "Bangalore"
    url = f"{base_url}/{location}?unitGroup=metric&key={api_key}&include=current"
    
    try:
        # Send the API request
        response = requests.get(url)
        
        # Check for a successful response
        if response.status_code == 200:
            weather_data = response.json()
            
            # Extract the required weather details
            current_conditions = weather_data['currentConditions']
            temp = current_conditions['temp']
            condition = current_conditions['conditions']
            feels_like = current_conditions['feelslike']
            humidity = current_conditions['humidity']
            
            # Prepare the weather report
            weather_report = (f"The current weather in Bangalore is {condition} with a temperature of {temp}°C. "
                              f"It feels like {feels_like}°C with a humidity of {humidity}%.")
            return weather_report
        else:
            return "I couldn't fetch the weather for Bangalore. Please try again later."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def fetch_and_speak_weather_bangalore():
    # Replace 'YOUR_API_KEY' with your actual API key
    api_key = "UBVTNPBUBTEQ3NSX3ZKDTMHCB"
    weather_report = get_weather_bangalore(api_key)
    speak(weather_report)  # Use your voice assistant's speak function


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
                    if any(keyword in individual_query for keyword in exit_phrases):
                        speak("Shutting down. Have a great day!")
                        # Exiting the app
                        #eel.close_browser_window()
                        exit(0)  # This will completely terminate the program
                        
                    elif 'play' in individual_query and 'on youtube' in individual_query:
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
                    elif 'pause' in query:
                        pyautogui.press("k")
                        speak("video paused")
                    elif 'play' in query:
                        pyautogui.press("k")
                        speak("video played")
                    elif 'mute' in query:
                        pyautogui.press("m")
                        speak("video muted")
                    elif 'unmute' in query:
                        pyautogui.press("m")
                        speak("video unmuted")
                    elif 'volume up' in query:
                        speak("turning volume up")
                        volumeup()
                    elif 'volume down' in query:
                        speak("turning volume down")
                        volumedown() 
                    elif 'increase brightness' in query:
                        speak("Increasing brightness")
                        increase_brightness()                       
                    elif 'check system resources' in query:
                        cpu = psutil.cpu_percent()
                        memory = psutil.virtual_memory().percent
                        speak(f"CPU usage is {cpu}% and memory usage is {memory}%")
                    elif 'install package' in query:
                        package_name = query.replace("install package", "").strip()
                        os.system(f"pip install {package_name}")
                        speak(f"Package {package_name} installed successfully")
                    # elif "send" in query and "email" in query:
                    #     speak("Whom do you want to send email to?")
                    #     statement=whatsapptakeCommand()
                    #     if is_in_email_contact(statement):
                    #         speak("What is the message you want to send?")
                    #         msg = whatsapptakeCommand()
                    #         to=get_email_address(statement)
                    #         send_email(to,msg)
                    #     else:
                    #         speak(get_email_address(statement))
                    elif "send" in query and "email" in query:
                        speak("Whom do you want to send the email to?")
                        recipient_name = whatsapptakeCommand()
    
                        if is_in_email_contact(cursor, recipient_name):  # Check if the contact exists
                            recipient_email = get_email_address_from_db(cursor, recipient_name)
        
                            speak("What is the message you want to send?")
                            msg = whatsapptakeCommand()
        
                            sender_email = "1da21cs066.cs@drait.edu.in"
                            sender_password = "wziftbxtqpngzaxt"  # Replace with environment variable in production
        
                            send_email(recipient_email, msg, sender_email, sender_password)
                            speak("Email sent successfully!")
                        else:
                            speak(f"{recipient_name} is not in the contact list. Please add them first.")
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
                    elif "weather" in query or "temperature" in query:
                        speak("Fetching the current weather details for Bangalore...")
                        fetch_and_speak_weather_bangalore()
                    elif "internet speed" in query:
                        wifi = speedtest.Speedtest()
                        wifi.get_best_server()  # Find the best server based on ping
                        download_net = wifi.download() / 1048576  # Convert from bits to Megabytes
                        upload_net = wifi.upload() / 1048576     # Convert from bits to Megabytes
                        print(f"Wifi Download Speed is: {download_net:.2f} Mbps")
                        print(f"Wifi Upload Speed is: {upload_net:.2f} Mbps")
                        speak(f"Your WiFi download speed is {download_net:.2f} Mbps")
                        speak(f"Your WiFi upload speed is {upload_net:.2f} Mbps")
                    elif "shutdown the system" in query:
                        speak("Shutting down the system.")
                        os.system("shutdown /s /t 1")  # Shutdown command
                    elif "news" in query or "current news" in query:
                        speak("Fetching the latest news...")
                        get_current_news()
                    elif "cricket score" in query:
                        try:
                            # CricAPI endpoint and your API key
                            api_key = "4ffb8366-a0fb-4e39-8775-fbe40f05ddde"  # Replace with your CricAPI key
                            url = f"https://api.cricapi.com/v1/cricScore?apikey={api_key}"

                            # Fetch data from CricAPI
                            response = requests.get(url)
                            data = response.json()

                            # Check if the request was successful
                            if data["status"] == "success" and "data" in data:
                                matches = data["data"]

                                # Flag to check if live matches exist
                                found_match = False

                                # First, search for a live match
                                for match in matches:
                                    if match["status"] == "live" and "score" in match:
                                        team1 = match["teams"][0]
                                        team2 = match["teams"][1]

                                        score1 = match.get("score", [])[0].get("r", "N/A")
                                        wickets1 = match.get("score", [])[0].get("w", "N/A")
                                        overs1 = match.get("score", [])[0].get("o", "N/A")

                                        score2 = match.get("score", [])[1].get("r", "N/A")
                                        wickets2 = match.get("score", [])[1].get("w", "N/A")
                                        overs2 = match.get("score", [])[1].get("o", "N/A")

                                        # Prepare live match message
                                        score_message = (
                                            f"Here is the live cricket update. {team1}: {score1}/{wickets1} in {overs1} overs, "
                                            f"and {team2}: {score2}/{wickets2} in {overs2} overs."
                                        )
                                        print(score_message)
                                        speak(score_message)
                                        found_match = True
                                        break  # Stop once a live match is found

                                # If no live match is found, fetch the most recent completed match
                                if not found_match:
                                    for match in matches:
                                        if match["status"] == "completed" and "score" in match:
                                            team1 = match["teams"][0]
                                            team2 = match["teams"][1]

                                            score1 = match.get("score", [])[0].get("r", "N/A")
                                            wickets1 = match.get("score", [])[0].get("w", "N/A")
                                            overs1 = match.get("score", [])[0].get("o", "N/A")

                                            score2 = match.get("score", [])[1].get("r", "N/A")
                                            wickets2 = match.get("score", [])[1].get("w", "N/A")
                                            overs2 = match.get("score", [])[1].get("o", "N/A")

                                            # Prepare completed match message
                                            score_message = (
                                                f"The latest completed match update: {team1} scored {score1}/{wickets1} in {overs1} overs, "
                                                f"and {team2} scored {score2}/{wickets2} in {overs2} overs."
                                            )
                                            print(score_message)
                                            speak(score_message)
                                            found_match = True
                                            break  # Stop once the latest match is found

                                # If no matches are found
                                if not found_match:
                                    no_match_message = "I couldn't find any recent cricket matches at the moment."
                                    print(no_match_message)
                                    speak(no_match_message)

                            else:
                                raise ValueError("Failed to fetch cricket data from CricAPI.")

                        except Exception as e:
                            error_message = "I couldn't fetch the cricket score at the moment. Please try again later."
                            print(f"Error: {str(e)}")
                            speak(error_message)


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
                            eel.code()
                            eel.display_generated_code(result)
                            if intention == "D":
                                speak(result)
                            elif intention != "Y" and intention != "E":
                                print(result)
                                eel.DisplayMessage(result)
                                result = result.split("!!")[0]
                                #speak(result)
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