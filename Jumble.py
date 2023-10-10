#***************************************************************#
#                  .                        *                *  #
#                *          MADE BY            .                #
#        *           _____,    _..-=-=-=-=-====--,  *   .       #
#       _         _.'a   /  .-',___,..=--=--==-'`               #
#      ((        ( _     \ /  //___/-=---=----'                 #
#       `         ` `\    /  //---/--==----=-'                  #
#             ,-.    | / \_//-_.'==-==---='       *             #
#      *     (.-.`\  | |'../-'=-=-=-=--'                   .    #
#      .      (' `\`\| //_|-\.`;-~````~,        _               #
#                   \ | \_,_,_\.'        \     .'_`\            #
#     *             `\            ,    , \    || `\\            #
#                 .   \    /   _.--\    \ '._.'/  / |         * #
#                     /  /`---'   \ \   |`'---'   \/            #
#          *         / /'          \ ;-. \                      #
#                 __/ /      *    __) \ ) `|            *       #
#    .           ((='--;)      .  (,___/(,_/                    #
#                *                                        .   . #
#       *                David Mojica S.E                       #
#          GitHub: https://github.com/DavidMojicaDev            #
#     .         Gmail : davidmojicav@gmail.com                  #
#---------------------------------------------------------------#
#            Release version: 1.3 - 10/10/23 (thursday)         #
#***************************************************************#
#------------------------------------------------------------------------------------
#Imports
#------------------------------------------------------------------------------------
#Python system libs
import asyncio
import json
import os
#Discord libs
import discord
from discord.ext import commands
from discord.ext.commands import errors
from c_match import Match
from ds_prints import Crear_Respuesta
#------------------------------------------------------------------------------------
#Variables Globales
#------------------------------------------------------------------------------------
#---Bot---#
file_config_bot     = "config_bot/config_bot.json"
template_config_bot = {"prefix" : "/", "token": ""}
bot                 = None

#---Jumble---#
tiempo_partida   = 180
tiempo_partida_c = 180
timeout_menu     = 10 #Expand

#Active
active_matches       = {}

#Messages
msg_menu = { 'head': "| JUMBLE |" , 'body': "Please select your languaje (give me a number):\n1: English\n2: Español\n3: Portuguese\n0: Exit"}
msg_4    = {'head': 'Stopped match', 'body': 'The match has been stoped.'}
msg_5    = {'head': 'Reseted', 'body': 'The match is reestarting...'}
msg_6    = {'head': 'Set time', 'body': 'The time was set in: '}

#Errors
error_1 = {'head': 'Think faster next time!', 'body' : 'You have took too long to respond.'}
error_2 = {'head': 'Match cancelled', 'body': 'You have cancelled the match.'}
error_3 = {'head': 'Cannot start a match now', 'body': 'Right now there is another game in progress'}
error_4 = {'head': 'You cant stop a match now', 'body': "You can't stop a match due to none match has started."}
error_5 = {'head': "You can't reset a match now", "body": "You can't reset a match due to none match has started."}
error_6 = {'head': "You can't set time to the match now", 'body': "There is not a active match."}
error_7 = {'head': 'Invalid option', 'body': 'I have displayed some valid options and you have not said any of these. Type %jumble again.'}
error_8 = {'head': "Not Match Leader", 'body': 'Only the match leader can change the match time.'}
error_9 = {'head': "Incorrect data-type", 'body': 'You have provided a letter when only numbers were expected, or vice versa'}
error_10 = {'head': "Null time", 'body': 'Please provide the number of seconds to set the match time.'}

#------------------------------------------------------------------------------------
#Main loop
#------------------------------------------------------------------------------------
def main():
    try:
        if os.path.exists(file_config_bot):
            with open(file_config_bot, encoding="utf-8") as f:
                config_bot = json.load(f)
        else:
            with open(file_config_bot, 'w', encoding="utf-8") as f:
                json.dump(template_config_bot, f, ensure_ascii=False)
                
        #Configuración inicial del bot
        prefix            = config_bot["prefix"]
        token             = config_bot["token"]
        desc              = config_bot["desc"]
        intents           = discord.Intents.all()
        intents.presences = True
        intents.members   = True
        global bot
        bot               = commands.Bot(command_prefix = prefix, intents = intents, description= desc)
        
        #------------------------------------------------------------------------------------
        #Comandos
        #------------------------------------------------------------------------------------
        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, errors.MissingRequiredArgument):
                await ctx.send(embed=Crear_Respuesta(error_10["head"], error_10["body"]).enviar)
        #---Jumble---#
        #DISABLED TEMPORARY
        # @bot.command(name="time", help="Set the time (in seconds) for the Jumble match.")
        # async def time(ctx, seconds: int):
        #     server_id = ctx.guild.id
        #     query_user = ctx.author.id

        #     if server_id not in active_matches:
        #         await ctx.send(embed=Crear_Respuesta(error_6["head"], error_6["body"]).enviar)
        #         return

        #     if query_user != active_matches[server_id].match_leader:
        #         await ctx.send(embed=Crear_Respuesta(error_8["head"], error_8["body"]).enviar)
        #         return

        #     await active_matches[server_id].start(ctx, bot, seconds)
        #     await ctx.send(embed=Crear_Respuesta(f'{essentials.num_to_emoji(msg_6["head"])}s', msg_6["body"]).enviar)

        @bot.command(name="reset", help="Restarts a jumble match.")
        async def reset(ctx):
            server_id = ctx.guild.id
            if server_id in active_matches:
                active_matches[server_id].time = 0
                active_matches[server_id].active_match = False
                await ctx.send(embed = Crear_Respuesta(msg_5["head"], msg_5["body"]).enviar)
                active_matches.pop(server_id, None)
                await jumble(ctx)                
            else:
                await ctx.send(embed = Crear_Respuesta(error_5["head"], error_5["body"]).enviar)
    
        @bot.command(name="stop", help="Stops a Jumble match")
        async def stop(ctx):
            server_id = ctx.guild.id
            global active_matches
            if server_id in active_matches:
                active_matches[server_id].time = 0
                active_matches[server_id].active_match = False
                await ctx.send(embed = Crear_Respuesta(msg_4["head"], msg_4["body"]).enviar)
                await active_matches[server_id].end(ctx)
                active_matches.pop(server_id, None)
            else:
                await ctx.send(embed = Crear_Respuesta(error_4["head"], error_4["body"]).enviar)

        @bot.command(name="jumble", help="Starts a Jumble match.")
        async def jumble(ctx):
            server_id = ctx.guild.id
            if server_id in active_matches:
                await ctx.send(embed=Crear_Respuesta(error_3["head"], error_3["body"]).enviar)
            else:
                # Menu
                await ctx.send(embed=Crear_Respuesta(msg_menu["head"], msg_menu["body"]).enviar)

                def check(message):
                    return message.author == ctx.author

                try:
                    lang = await bot.wait_for("message", check=check, timeout=timeout_menu)
                    lang = lang.content  # acceder al valor del mensaje
                    match = Match(tiempo_partida_c, lang, author_id=ctx.author.id)
                    status = await match.load(ctx, lang)
                    error_message = globals().get(f"error_{status}", None)
                    if error_message:
                        await ctx.send(embed=Crear_Respuesta(error_message["head"], error_message["body"]).enviar)
                    else:
                        active_matches[server_id] = match
                        server_id = await match.start(ctx, bot)
                        active_matches.pop(server_id, None)

                except asyncio.TimeoutError:
                    await ctx.send(embed=Crear_Respuesta(error_1["head"], error_1["body"]).enviar)
                    
        #Encender el bot
        bot.run(token)
    except (Exception) as error:
        print(repr(error))
if __name__ == "__main__":
    main()