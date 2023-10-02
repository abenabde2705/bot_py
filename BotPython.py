import discord #pip install discord
import asyncio
import pyexcel_ods as ods #pip install pyexcel_ods
import json
import os
import re
from discord.ext import commands
from discord.ext.commands import Bot
from collections import OrderedDict

global GROUPE
GROUPE = None

"""
#Gestion des insultes
if os.path.exists(os.getcwd()+"/config.json"):
    with open(os.getcwd()+"/config.json") as f:
        configData = json.load(f)
bannedWords = configData["bannedWords"]

#Gestion de la commande addbad
@bot.command(name = "addbad")
@commands.has_permissions(manage_roles=True)
async def addbad(ctx, word):
    if word.lower() in bannedWords:
        await ctx.send("Mot déjà banni")
    else:
        bannedWords.append(word.lower())
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        await ctx.message.delete()
        await ctx.send("Mot ajouté à la liste des mots bannis.")

#Gestion de la commande removebad
@bot.command(name = "removebad")
@commands.has_permissions(manage_roles=True)
async def removebad(ctx, word):
    if word.lower() in bannedWords:
        bannedWords.remove(word.lower())
        with open("./config.json", "r+") as f:
            data = json.load(f)
            data["bannedWords"] = bannedWords
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        await ctx.message.delete()
        await ctx.send("Mot supprimé à la liste de mots bannis.")
    else:
        await ctx.send("Mot non banni.")

@bot.event
async def on_message(message):
    messageAuthor = message.author
    if bannedWords != None and (isinstance(message.channel, discord.channel.DMChannel) == False):
        for bannedWord in bannedWords:
            if re.search(fr'\b({bannedWord})\b', message.content.lower()) is not None:
                await message.delete()
                await message.channel.send(
                    f"{messageAuthor.mention} Ton message a été supprimé car il contient un mot banni")
    await bot.process_commands(message)
"""

#Permet de récupéré les informations présent dans la "base de données"
def read(feuille):
    try:
        data = ods.get_data(os.getcwd()+"/sauv.ods")
        lecture = data[feuille]
        return lecture
    except FileNotFoundError:
        print("Le fichier n'a pas été trouvé")

#Permet l'écriture d'informations dans la "base de données"
def write():
    global GROUPE
    try:
        oldData = ods.get_data(os.getcwd()+"/sauv.ods")
        oldFeuille = oldData["QCM"]
        data = OrderedDict()
        data.update({"groupe": GROUPE})
        data.update({"QCM": oldFeuille})
        ods.save_data(os.getcwd()+"/sauv.ods", data)
    except PermissionError:
        print("Permission refusé, le fichier est peut être ouvert. Merci de le fermer")

bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())
bot.remove_command("help")

#Informe lorsque le bot est allumé
@bot.event
async def on_ready():
    print("Le bot est prêt !")
    await bot.change_presence(activity=discord.Game(f'{bot.command_prefix}help'))

#Gestion de la commande help
@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(colour=discord.Colour.purple())
    embed.set_author(name='Liste des fonctionnalités')

    embed.add_field(name="‎ ", value="--- Les commandes disponible pour tout le monde ---", inline=False)
    embed.add_field(name="**!help**", value="Voir la liste des commandes", inline=False)
    embed.add_field(name="**!rappel**", value="Ecrit un message qui s'envera après un temps donné", inline=False)
    embed.add_field(name="**!sondage**", value="Crée un sondage (uniquement en interrogation totale)", inline=False)
    #embed.add_field(name="**!ticket**", value="Crée un ticket (demande d'aide ou information sur un problème / bug)", inline=False) #non fait
    #embed.add_field(name="**!QCM**", value="Propose des QCM pour s'entraîner dans certaines matières", inline=False) #non fait
    embed.add_field(name="**!groupe**", value="permet de gérer des groupe", inline=False)
    
    if ctx.message.author.guild_permissions.manage_roles:
        embed.add_field(name="‎ ", value="--- Les commandes de gestion de rôle ---", inline=False)
        embed.add_field(name="**!verifMuted**", value="Verifie si le rôle Muted est correctement initialisé (à utiliser si création de salon lorsque le bot n'est pas connecté)", inline=False)
        embed.add_field(name="**!verifGroupe**", value="regarde les groupes existant dans la BDD (à utiliser quand le bot se reconnecte)", inline=False)
        embed.add_field(name="**!sauvGroupe**", value="sauvegarde les groupes existant dans la BDD (à utiliser quand le bot va s'éteindre)", inline=False)
        embed.add_field(name="**!mute**", value="Rend muet quelqu'un", inline=False)
        embed.add_field(name="**!unmute**", value="Rend la parole a quelqu'un", inline=False)
    if ctx.message.author.guild_permissions.manage_messages:
        embed.add_field(name="‎ ", value="--- La commande de gestion de message ---", inline=False)
        embed.add_field(name="**!clear**", value="Efface un certain nombre de message", inline=False)
    embed.add_field(name="‎ ", value="--- Les fonctionalité passives ---", inline=False)
    embed.add_field(name="**Welcome / Goodbye**", value="Informe des membres qui arrivent ou quittent le serveur", inline=False)
    embed.add_field(name="**Create channel**", value="Crée un vocal quand on le rejoind (se supprime quand on le quitte)", inline=False)
    #embed.add_field(name="**Modération chat**", value="évite les grossièretés dans les mesages", inline=False) #non fonctionnelle
    await ctx.send(embed=embed)

#Gestion de la commande verifMuted
@bot.command(name="verifMuted")
@commands.has_permissions(manage_roles=True)
async def verifMuted(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if role == None:
        role = await ctx.guild.create_role(name="Muted", colour=discord.Colour(0xff00ff))
        await ctx.send("Le rôle Muted a été créé")
    for channel in ctx.guild.channels:
        if type(channel) is discord.channel.TextChannel:
            perms = channel.overwrites_for(role)
            perms.send_messages=False
            await channel.set_permissions(role, overwrite=perms)
    await ctx.send("Tous les salons utilise le rôle Muted")

#Gestion de la commande verifGroupe
@bot.command(name="verifGroupe")
@commands.has_permissions(manage_roles=True)
async def verifGroupe(ctx):
    global GROUPE
    if GROUPE:
        await ctx.send("déjà initialisé, pour sauvegarder faites !sauvGroupe")
    else:
        GROUPE = read("groupe")

#Gestion de la commande sauvGroupe
@bot.command(name="sauvGroupe")
@commands.has_permissions(manage_roles=True)
async def sauvGroupe(ctx):
    global GROUPE
    if GROUPE:
        write()
    else:
        await ctx.send("il n'y a rien, utilisé verifGroupe avant !")

#Gestion de la commande mute
@bot.command(name="mute")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member=None, time: int=None):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if role == None:
        await ctx.send("Rôle Muted introuvable, création du rôle...")
        role = await ctx.guild.create_role(name="Muted", colour=discord.Colour(0xff00ff))
        for channel in ctx.guild.channels:
            if type(channel) is discord.channel.TextChannel:
                perms = channel.overwrites_for(role)
                perms.send_messages=False
                await channel.set_permissions(role, overwrite=perms)
        await ctx.send("Le rôle Muted a été créé")
    if member == None:
        await ctx.send(f"{bot.command_prefix}mute [membre (avec un @)] [temps (en minute (si non renseigner: infini))]")
    else:
        if member.guild_permissions.manage_roles:
             await ctx.send(f"{member.display_name} ne peut pas être mute")
        else:
            test = discord.utils.get(member.roles, name='Muted')
            if test != None:
                await ctx.send(f"{member.display_name} est déjà mute")
            else:
                if time == None:
                    await member.add_roles(role)
                    await ctx.send(f"{member.display_name} a été réduit au silence")
                else:
                    await member.add_roles(role)
                    await ctx.send(f"{member.display_name} a été réduit au silence pendant {time} minutes")
                    await asyncio.sleep(time*60)
                    await member.remove_roles(role)

#Gestion de la commande unmute
@bot.command(name="unmute")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member=None):
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if role == None:
        await ctx.send(f"Le rôle 'Muted' n'existe même pas...")
    elif member == None:
        await ctx.send(f"{bot.command_prefix}unmute [membre (avec un @)]")
    else:
        enlever = discord.utils.get(member.roles, name='Muted')
        if enlever == None:
            await ctx.send(f"{member.display_name} n'est pas mute")
        else:
            await member.remove_roles(enlever)
            await ctx.send(f"{member.display_name} peut de nouveau parler")

#Gestion de la commande rappel
@bot.command(name="rappel")
async def rappel(ctx, time = None, *, text=None):
    if time == None:
        await ctx.send(f"{bot.command_prefix}rappel [jour'd'heure'h'minute] [texte (à afficher une fois le temps écoulé)]")
    else:
        try:
            temps = []
            temps.append(time.split("d")[0])
            if temps[0] == "":
                temps[0] = "0"
            if "h" in temps[0]:
                temps = ["0", temps[0]]
            else:
                temps.append(time.split("d")[1])
            if "h" in temps[1]:
                temps.append(temps[1].split("h")[1])
            else:
                temps.append(0)
            temps[1] = temps[1].split("h")[0]
            if temps[1] == "":
                temps[1] = 0
            if temps[2] == "":
                temps[2] = 0
            temps[0] = int(temps[0])
            temps[1] = int(temps[1])
            temps[2] = int(temps[2])
            if len(temps) != 3 or 0>temps[0] or 0>temps[1] or 23<temps[1] or 0>temps[2] or temps[2]>59:
                int("temps incorrecte")
            attendre = temps[0]*86400+temps[1]*3600+temps[2]*60
            await ctx.send(f"Le rappel sonnera dans {temps[0]} jours, {temps[1]} heures et {temps[2]} minutes")
            await asyncio.sleep(attendre)
            await ctx.send(f"Rappel de {ctx.message.author.display_name}: {text}")
        except:
            await ctx.send("Le temps rentré est incorrecte, il faut faire: jour'd'heure'h'min, exemple: !rappel 1d16h26 blablabla")

#Gestion de la commande clear
@bot.command(name = "clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx , nbr = None):
    if nbr == None:
        await ctx.send(f"{bot.command_prefix}clear [nombre (maximum 50)]")
    else:
        try:
            nv = int(nbr)
            if nv < 0:
                await ctx.send("le nombre est négatif")
            else:
                if nv > 50:
                    nv = 50
                await ctx.channel.purge(limit = nv + 1)
        except:
            await ctx.send("entrez un nombre !!!")

#Gestion de la commande groupe
@bot.command(name="groupe")
async def groupe(ctx, action=None, nom=None, member: discord.Member=None):
    global GROUPE
    if not(GROUPE):
        await ctx.send("la gestion des groupes n'a pas était initialisé avec verifGroupe !")
    else:
        if action == None:
            await ctx.send(f"{bot.command_prefix}groupe [action (create, add, remove, delete)] [nom (sans espace)] [member (si add ou remove)]")
        elif nom == None:
            await ctx.send("Merci de préciser le goupe !")
        else:
            if action == "create":
                existe = False
                for ligne in range(1,len(GROUPE)):
                    if GROUPE[ligne][0] == nom:
                        await ctx.send("Il y a déjà un groupe à ce nom")
                        existe = True
                if not(existe):
                    GROUPE.append([nom,str(ctx.author.id)])
                    role = await ctx.guild.create_role(name="groupe: "+nom, colour=discord.Colour(0xffffff))
                    await ctx.author.add_roles(role)
            elif action == "add":
                existe = False
                for ligne in range(1,len(GROUPE)):
                    if GROUPE[ligne][0] == nom and GROUPE[ligne][1] == str(ctx.author.id):
                        if str(member.id) in GROUPE[ligne]:
                            await ctx.send("Cette personne est déjà dans le groupe")
                        else:
                            GROUPE[ligne].append(str(member.id))
                            role = discord.utils.get(ctx.guild.roles, name="groupe: "+nom)
                            await member.add_roles(role)
                        existe = True
                if not(existe):
                    await ctx.send("Tu n'as pas de groupe à ce nom")
            elif action == "remove":
                existe = False
                for ligne in range(1,len(GROUPE)):
                    if GROUPE[ligne][0] == nom and GROUPE[ligne][1] == str(ctx.author.id):
                        if str(member.id) in GROUPE[ligne]:
                            if GROUPE[ligne][1] != str(ctx.author.id):
                                GROUPE[ligne].remove(str(member.id))
                                role = discord.utils.get(ctx.guild.roles, name="groupe: "+nom)
                                await member.remove_roles(role)
                            else:
                                await ctx.send("Tu ne peux pas quitter les groupes dont tu es le chef")
                        else:
                            await ctx.send("Cette personne n'est pas dans le groupe")
                        existe = True
                if not(existe):
                    await ctx.send("Tu n'as pas de groupe à ce nom")
            elif action == "delete":
                suppr = -1
                for ligne in range(1,len(GROUPE)):
                    if GROUPE[ligne][0] == nom and GROUPE[ligne][1] == str(ctx.author.id):
                        suppr = ligne
                if suppr == -1:
                    await ctx.send("Vous n'avez pas de groupe à ce nom")
                else:
                    del GROUPE[suppr]
                    role = discord.utils.get(ctx.guild.roles, name="groupe: "+nom)
                    await role.delete()
            else:
                await ctx.send("action inconnu: (create, add, remove, delete)")

#Gestion de la commande sondage
@bot.command(name = "sondage")
@commands.has_permissions(manage_messages=True)
async def sondage(ctx,* ,question=None):
    embed=discord.Embed(title= question , description=f"yes:👍\n\n No:👎", color=discord.Color.blue())
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

#Permet le fonctionnement du rôle Muted lors de la création d'un nouveau salon textuel
@bot.event
async def on_guild_channel_create(channel):
    role = discord.utils.get(channel.guild.roles, name='Muted')
    if role != None:
        if type(channel) is discord.channel.TextChannel:
            perms = channel.overwrites_for(role)
            perms.send_messages=False
            await channel.set_permissions(role, overwrite=perms)

#Gestion des salons "create channel"
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        if after.channel.name.lower() == "create channel":
            category =  discord.utils.get(member.guild.categories, id=after.channel.category_id)
            channel = await member.guild.create_voice_channel("Salon Temporaire", category=category)
            await member.move_to(channel)
    if before.channel is not None:
        if before.channel.name == "Salon Temporaire" and not before.channel.members:
            await before.channel.delete()

#Gestion des bienvenu
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='bienvenue-et-règles')
    embed=discord.Embed(colour = discord.Colour.green(),title=f"Hey there {member.name} ", description=f"Enjoy your stay in Our  {member.guild.name} server! :hugging:") # F-Strings!
    embed.set_thumbnail(url=member.display_avatar) # Set the embed's thumbnail to the member's avatar image!
    await channel.send(embed=embed)
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.set_author(name="Our Rules")
    embed.add_field(name="**Rule #01:**", value="\t Introduce your self in discussion channel", inline=False)
    embed.add_field(name="**Rule #02:**", value="\t Be nice with other members and help them if needed", inline=False)
    embed.add_field(name="**Rule #03:**", value="\t No curse words in our server", inline=False)
    embed.add_field(name="**Rule #04:**", value="\t Each time you break our rules you'll get banned temporary for 1 day (ps: 3 times banned = **permanent ban**)", inline=False)
    await channel.send(embed=embed)
    
#Gestion des au revoir
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='bienvenue-et-règles')
    embed=discord.Embed(colour = discord.Colour.red(),title=f"{member.name} Just left us",description=f"See you soon buddy! :pleading_face:")
    embed.set_thumbnail(url=member.display_avatar)
    await channel.send(embed=embed)

#Gestion des erreurs
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Tu n'as pas les permissions pour effectuer cette commande !")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Le membre discord n'a pas était trouvé !")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("La commande n'a pas été trouvé")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Un paramètre de la commande n'est pas du bon type !")
    else:
        raise error

bot.run("MTAzNDc0MTgxMzUyNjkyOTQ0OQ.GnlZYn.c599FSaBsVOcJJPDYszzR4J1WOxhO9bs6KYY8w")
