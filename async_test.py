# -*- coding: utf-8 -*-

import discord
import re
import time
import pandas as pd
import random
import threading
from discord.ext import tasks
client = discord.Client()
# emoji=discord.emoji()
emojis_dict = {"0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣",
               "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣"}
liste_lettre = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", " ","`"]
liste_mots = [" ",""]
fichier = open("data.txt", "r")
liste_fautes=[]
usefull = ["Username","UserID","Nbmots","Nbfautes","Timestamp"]

with open("token.txt","r") as f:
    token = f.readline()




try:
    dfMessage = pd.read_csv("data/BDD_message.csv")
except:
    dfMessage = pd.DataFrame({"Username": [],"UserID":[], "Nbmots":[], "Nbfautes": [],"Timestamp":[]})
    dfMessage.to_csv('data/BDD_message.csv')

for line in fichier.readlines():
    liste_mots.append(line.strip())


def beautify_text(text):
    text_sortis = ""
    for lettre in text:
        if lettre .lower() in liste_lettre:
            text_sortis += lettre
        else:
            text_sortis += " "
    return text_sortis


async def corrige_fautes(message):
    global dfMessage
    if message.author == client.user:
        return
    if message.author.bot:
        return
    message_txt = message.content.replace("é", "e").replace("è", "e").replace("ë", "e").replace(
        "à", "a").replace("ç", "c").replace("ê", "e").replace("â", "a").replace("î", "i").replace("ï", "i").replace("ô","o")
    message_txt = message_txt.replace("É", "E").replace("È", "e").replace("Ë", "e").replace(
        "À", "a").replace("Ç", "c").replace("Ê", "e").replace("Â", "a").replace("Î", "i").replace("Ï", "i").replace("Ô", "O")
    message_txt = beautify_text(message_txt)
    message_txt = re.split(" |'", message_txt)

    i = 0
    d = 0
    print("------")
    for mot in message_txt:
        mot.replace(" ","")
        if mot in liste_mots:
            pass
        elif mot[0].lower() != mot[0]:
            pass
        elif len(mot) <2:
            pass
        elif mot in ["http","https", "```"]:
            break
        elif mot[0] == "`":
            break
        else:
            print(mot)
        #    await client.send_message(694926082763259954,str(message.author)+" a fait une faute en écrivant: "+mot)
            liste_fautes.append([message.author,mot])
            i += 1
        d += 1
    final = ""
    nb_de_mot = len(message_txt)
    timestamp = time.time()
    dfMessage =dfMessage.append({"Username":str(message.author.name),"UserID":int(message.author.id), "Nbmots": int(nb_de_mot),"Nbfautes":int(i),"Timestamp":int(time.time())},ignore_index=True)
    if random.random() > 0.9:
        dfMessage[usefull].to_csv("data/BDD_message.csv")
    if i == 0:
        print("OK")
    else:
        if i > 7:
            auteur = message.author
            auteur = auteur.id

            await message.channel.send("<@"+str(auteur)+"> est une sous-merde il ne sais pas aligner 7 mot correctement. "+str(i)+" fautes en un message t'éxagère franchement")
        i = str(i)
        i = [elt for elt in i]
        for e in i:
            b = emojis_dict[e]
            await message.add_reaction(b)


@tasks.loop(minutes = 5)
async def print_leaderboard_loop(h_in_past=24):
    if time.localtime().tm_hour != 22 or time.localtime().tm_hour != 10:
        return


    timeMin = time.time()-(60*60*h_in_past)
    dfMessageDelta = dfMessage[dfMessage["Timestamp"] > timeMin]
    dfResults = pd.DataFrame({"Username":[],"NbmotMoyen":[],"MotsFaux":[],"NbMessages":[]})
    dfMessageDelta
    for personne in dfMessageDelta["UserID"].unique():
        mask = dfMessageDelta["UserID"]==personne
        username = dfMessageDelta["Username"][mask].values[-1]
        nombre_mot_moyen = dfMessageDelta["Nbmots"][mask].mean()
        nombre_fautes_moyen = dfMessageDelta["Nbfautes"][mask].mean()
        nombre_message = len(dfMessageDelta[mask])
        print("------")
        print(username)
        nb_mot_moyen = round(nombre_mot_moyen,1)
        print("nb mot moyen : ",nb_mot_moyen)
        mots_faut = round(nombre_fautes_moyen/nombre_mot_moyen*100,2)
        print("Mots faux : ", mots_faut , "%")
        print("nb messages : ", nombre_message)
        dfResults = dfResults.append({"Username":username,"NbmotMoyen":nb_mot_moyen,"MotsFaux":mots_faut,"NbMessages":nombre_message}, ignore_index=True)



    total_mots = dfMessageDelta["Nbmots"].sum()
    if total_mots == 0:
        total_mots +=1

    nombre_message_total = dfMessageDelta["Username"].count()
    nombre_fautes_total = dfMessageDelta["Nbfautes"].sum()

    fautes_globales = round(nombre_fautes_total/total_mots*100,2)
    fautes_globales





    discalified = dfResults["Username"][dfResults["NbMessages"] < 20].values




    text = ""
    text += "```Markdown\n#Lexique leaderboard```\n"
    place = 1
    classment_mot_faux= dfResults.sort_values("MotsFaux").values
    for x in classment_mot_faux:
        text += "- N°{} : __{}__    avec **{}%**  de fautes\n".format(place,x[0],x[2])
        place += 1
    text += "\n"


    text += "##Activitée leaderboard##\n"
    classment_nb_message = dfResults.sort_values("NbMessages", ascending=False).values
    place = 1
    for x in classment_nb_message:
        text += "- N°{} : __{}__    avec **{}** messages\n".format(place,x[0],int(x[3]))
        place += 1
    text += "\n"
    text+= "##Autres Stats##\n"
    text+= "* __{}__ mot ,".format(total_mots)
    text += "__{}__ fautes ".format(nombre_fautes_total)
    text += "(__{}%__)\n".format(int(nombre_fautes_total/total_mots*100))
    text += "* __{}__ message \n".format(nombre_message_total)
    try:
        text += "* __{}__ à monopolisé **{}%** du temps de parole\n".format(classment_nb_message[0][0], int(classment_nb_message[0][3]/nombre_message_total*100))
    except:
        pass


    channel = client.get_channel(689460081766694991)


    await channel.send(text)


@client.event
async def on_message(message):
    global liste_fautes

    if message.content == "statut":
        print("changement de statut")
        await client.change_presence(activity=discord.Game(name='à corriger des copies'))
    elif message.channel.id == 694926082763259954 or message.channel.id == 696695647310446633:
        print("pass")
    else:
        await corrige_fautes(message)
#    if message.author.id == 323486943331483660:
#        await message.add_reaction("💩")
#####    if len(liste_fautes)>10:
####        channel = client.get_channel(694926082763259954)
###        for fautes in liste_fautes:
##            await channel.send(str(fautes[0])+" a fait une faute en écrivant: "+fautes[1])
#        liste_fautes=[]





@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print_leaderboard_loop.start()
    print('------')




print("EE",token.replace("\n",""),"EE")
client.run(token.replace("\n",""))
