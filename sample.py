import aiml
import os
import random
import time
import pyttsx3
from weather import Weather
from news import News
from google import Search
from DBconnect import *
import signal
import datetime
import sys
import string

def evaulateExpression(fexp):
    expstr = fexp.replace(' ','')
    return eval(expstr)


# Create the kernel and learn AIML files
kernel = aiml.Kernel()
engine = pyttsx3.init()
obj = DBconnect()
obj.getConnection('chatbot.db')
obj.putQuery("CREATE TABLE IF NOT EXISTS chat_history ( qid integer PRIMARY KEY AUTOINCREMENT,question text NOT NULL, response text);")
obj.putQuery("CREATE TABLE IF NOT EXISTS retrieved ( qid integer PRIMARY KEY AUTOINCREMENT, question text NOT NULL, response text);")
insertQuery1b = "INSERT INTO chat_history ( question, response ) VALUES ("
insertQuery2b = "INSERT INTO retrieved (question, response ) VALUES ("


if os.path.isfile("bot_brain.brn"):
    pass
if True:
    kernel.bootstrap(learnFiles = "sample.xml", commands = "load aiml b")
    kernel.saveBrain("bot_brain.brn")

querystring=""


# Handles CTRL+C
def sigint_handler(signum,frame):
    obj.closeConnection()
    exit()

def speakOut(output,voice):
    if voice:
        engine.say(output)
        engine.runAndWait()

voice=False
if len(sys.argv)==2 and sys.argv[1]=='--voice':
    voice=True

while True:
    signal.signal(signal.SIGINT, sigint_handler)
    message = input("Enter message: ")
    if len(message)<1 :
        continue
    if message == "quit" or message=="exit":
        obj.closeConnection()
        exit()
    elif message == "save":
        kernel.saveBrain("bot_brain.brn")
    else:
        
        kernel.setPredicate('ctype',0)
        bot_response = kernel.respond(message)

        if len(bot_response)<2:

            bot_response="Want me to google it?"
            print(bot_response)
            speakOut(bot_response,voice)

            kernel.setPredicate('topic',"eagertoknow")
            bot_response = input("User: ")
            
            if bot_response.lower()=="YES".lower():
                bot_response="Okay let me see..."
                print(bot_response)
                speakOut(bot_response,voice)
                s=Search.make_request(message)

                if s['success']:
                    s['d']=s['d'][:-10]
                    print(s['d'])
                    querystring=insertQuery2b+"\""+message+"\""+",\""+s['d']+"\");"
                    obj.putQuery(querystring)
                    speakOut(s['d'],voice)

                else:
                    print("Search Failed")
                    speakOut("Search Failed",voice)

            else:
                bot_response="Ok, tell me what it is: "
                print(bot_response)
                speakOut(bot_response,voice)
                
                bot_response = input()
                querystring=insertQuery2b+"\""+message+"\""+",\""+bot_response+"\");"
                obj.putQuery(querystring)

                print("Okay, thank you for telling me about it")
                speakOut("Okay, thank you for telling me about it",voice)

        else:
            #querystring=insertQuery1b+"\""+message+"\""+",\""+bot_response+"\");"
            #obj.putQuery(querystring)
            print(bot_response)        
            speakOut(bot_response,voice)
            bot_response+='\n'
            l=len(bot_response)
            inp = kernel.getPredicate('ctype')
            if inp=="1" :
                time.sleep(1)
                kernel.setPredicate('expression',str(evaulateExpression(kernel.getPredicate('expression'))))
                bot_response+=kernel.respond('results')
                bot_speech=bot_response[l:]

            elif inp=="2":
                time.sleep(1)
                num = random.randint(0,1)
                if num==1:
                    kernel.setPredicate('expression',"Heads")
                else:
                    kernel.setPredicate('expression',"Tails")

                bot_response+=kernel.respond('toss outcome')
                bot_speech=bot_response[l:]

            elif inp=='3' or inp=='4':
                time.sleep(1)
                uval = 6
                num = random.randint(1,6)
                if inp=="4":
                    uval = int(kernel.getPredicate('expression'))
                    num = random.randint(1,uval)
                kernel.setPredicate('expression',str(num))
                bot_response+=kernel.respond('die outcome')
                bot_speech=bot_response[l:]

            elif inp=='5' or inp=='6':
                if inp=='5':
                    city=kernel.getPredicate('home_city')
                    if city == "":
                        city="Secunderabad"
                else:
                    city=kernel.getPredicate('city')

                w=Weather.get_current_weather(city)
                if w['success']:
                    bot_response += "The weather in {} is {}. The temperature is {} with a minimum of {} and a maximum of {} celcius. The humidity is {}%.".format(
                        w['place'],w['desc'],w['temp'],w['temp_min'],w['temp_max'],w['humidity'])
                
                else:
                    bot_response+="Sorry, couldn't get the weather"

                bot_speech=bot_response[l:]

            elif inp=='7' or inp=='8' :
                if inp=='7':
                    city=kernel.getPredicate('home_city')
                    if city == "":
                        city="Secunderabad"
                else:
                    city=kernel.getPredicate('city')

                w=Weather.get_5_day_forecast(city)
                if w['success']:
                    bot_response+="The forecast for {} is as follows\n".format(w['place'])
                    for a in w['w']:
                        d=datetime.datetime.strptime(a['date'],"%Y-%m-%d %H:%M:%S").date()
                        bot_response+=("{}-{}-{}, {} with a temperature of {} celcius and humidity of {}%\n".format(d.day,d.month,d.year,a['desc'],a['temp'],a['humidity']))

                else:
                    bot_response+="Sorry, couldn't get the forecast"

                bot_speech=bot_response[l:]

            elif inp=='9' or inp=='10':
                news=kernel.getPredicate('news')
                if news!="":
                    if inp=='9':
                        n=News.get_india_top_headlines(news)
                    else:
                        n=News.get_world_top_headlines(news)
                else:
                    if inp=='9':
                        n=News.get_india_top_headlines()
                    else:
                        n=News.get_world_top_headlines()
                if n['success']:
                    bot_speech=""
                    for a in n['a']:
                        bot_response+="{}\n{}\n".format(a['title'],a['url'])
                        bot_speech+="{}\n".format(a['title'])
                    
                else:
                    bot_response+="Sorry, couldn't get the news"
                    bot_speech=bot_response[l:]

            else:
                querystring=insertQuery1b+"\""+message+"\""+",\""+bot_response+"\");"
                obj.putQuery(querystring)
                continue

            querystring=insertQuery1b+"\""+message+"\""+",\""+bot_response+"\");"
            obj.putQuery(querystring)
            print(bot_response[l:])
            speakOut(bot_speech,voice)