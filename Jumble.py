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
#            Release version: 1.0 - 26/08/23 (saturday)         #
#***************************************************************#
#------------------------------------------------------------------------------------
#Imports
#------------------------------------------------------------------------------------
#Python system libs
import asyncio
import random
import json
import os
import io
#Discord libs
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
#program libs
import essentials
from essentials import emoji_numbers, print_chars
from c_player import Player
from c_match import Match
from ds_prints import Crear_Respuesta
#------------------------------------------------------------------------------------
#Variables Globales
#------------------------------------------------------------------------------------
#---Bot---#
file_config_bot     = "config_bot/config_bot.json"
template_config_bot = {"prefix" : "%", "token": ""}
bot                 = None

#---Jumble---#
tiempo_partida   = 15
tiempo_partida_c = 15
tiempo_aviso     = 10  #Cada tiempo se le recordarán a los jugadores las letras que pueden usar y el tiempo que les queda.
# tiempo_contador  = None
file             = ""
consonants       = ""
vocals           = ""
timeout_menu     = 10 #Expand

#Active
active_matches       = {}
#Messages

msg_menu       = { 'head': "| JUMBLE |" , 'body': "Please select your languaje (give me a number):\n1: English\n2: Español\n0: Exit"}
msg_4          = {'head': 'Stopped match', 'body': 'The match has been stoped.'}
msg_5          = {'head': 'Reseted', 'body': 'The match is reestarting...'}
msg_6          = {'head': 'Set time', 'body': 'The time was set in: '}

#Errors
error_1        = {'head': 'Think faster next time!', 'body' : 'You have took too long to respond.'}
error_2        = {'head': 'Match cancelled', 'body': 'You have cancelled the match.'}
error_3        = {'head': 'Cannot start a match now', 'body': 'Right now there is another game in progress'}
error_4        = {'head': 'You cant stop a match now', 'body': "You can't stop a match due to none match has started."}
error_5        = {'head': "You can't reset a match now", "body": "You can't reset a match due to none match has started."}
error_6        = {'head': "You can't set time to the match now", 'body': "There is not a active match."}
error_7        = {'head': 'Invalid option', 'body': 'I have displayed some valid options and you have not said any of these. Type %jumble again.'}



#------------------------------------------------------------------------------------
#Clases
#------------------------------------------------------------------------------------

    
    
#------------------------------------------------------------------------------------
#Main loop
#------------------------------------------------------------------------------------
def main():
    #------------------------------------------------------------------------------------
    #Operaciones iniciales del bot con el archivo config_bot.json
    #------------------------------------------------------------------------------------
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
        #---Jumble---#
        # @bot.command(name="time", help="Set the time (in seconds) to the Jumble match.")
        # async def time(ctx, msg):
        #     global active_matches
        #     global tiempo_partida
            
        #     if active_matches:
        #         msg_user = int(msg.content)
        #         tiempo_partida = msg_user
        #         await ctx.send(embed = Crear_Respuesta(f'{num_to_emoji(msg_6["head"])}s', msg_6["body"]).enviar)

        #     else:
        #         await ctx.send(embed = Crear_Respuesta(error_6["head"], error_6["body"]).enviar)

        @bot.command(name="reset", help="Restarts a jumble match.")
        async def reset(ctx):
            server_id = ctx.guild.id
            global active_matches
            if active_matches[server_id]:
                await ctx.send(embed = Crear_Respuesta(msg_5["head"], msg_5["body"]).enviar)
                global tiempo_partida
                tiempo_partida = 0
                
                active_matches[server_id] = False
                await jumble(ctx)
            else:
                await ctx.send(embed = Crear_Respuesta(error_5["head"], error_5["body"]).enviar)
    
        @bot.command(name="stop", help="Stops a Jumble match")
        async def stop(ctx):
            server_id = ctx.guild.id
            global active_matches
            if active_matches:
                await ctx.send(embed = Crear_Respuesta(msg_4["head"], msg_4["body"]).enviar)
                global tiempo_partida
                tiempo_partida = 0
                
                active_matches[server_id] = False
            else:
                await ctx.send(embed = Crear_Respuesta(error_4["head"], error_4["body"]).enviar)

        
        @bot.command(name="jumble", help="Starts a Jumble match.")
        async def jumble(ctx):
            server_id = ctx.guild.id
            if server_id in active_matches:
                await ctx.send(embed = Crear_Respuesta(error_3["head"], error_3["body"]).enviar)
            else:
                #Jumble reiniciar variables           
                global tiempo_partida
                tiempo_partida = tiempo_partida_c
                
                global cant_validas
                cant_validas = 0
                
                global palabras_dichas
                palabras_dichas = 0 
                
                #--------------------------------------------------------------------------------
                #Menu
                #--------------------------------------------------------------------------------
                await ctx.send(embed = Crear_Respuesta(msg_menu["head"] , msg_menu["body"]).enviar)
                
                def check(message):
                    return message.author == ctx.author
                try:
                    lang = await bot.wait_for("message", check=check, timeout=timeout_menu)
                    lang = lang.content # acceder al valor del mensaje
                    match = Match(tiempo_partida_c, lang)
                    status = await match.load(ctx, lang)
                    if status != "0":
                        e = f"error_{status}"
                        if e in globals():
                            error_message = globals()[e]
                            await ctx.send(embed=Crear_Respuesta(error_message["head"], error_message["body"]).enviar)
                    else:
                        active_matches[server_id] = match
                        print(active_matches)
                        await __startgame__(ctx, match)
                    #------------------------------------------------------------------------------------
                    #CARGA - archivos externos
                    #------------------------------------------------------------------------------------       
                 
                except asyncio.TimeoutError:
                    await ctx.send(embed = Crear_Respuesta(error_1["head"], error_1["body"]).enviar)
                
        #Encender el bot
        bot.run(token)
    except (Exception) as error:
        print(repr(error))

#------------------------------------------------------------------------------------
#Match - Partida
#------------------------------------------------------------------------------------
async def __startgame__(ctx, match):
    """Inicia el juego y maneja la ejecución y el flujo de mensajes.

    Args:
        cant_validas (int): Cantidad de palabras válidas disponibles para el juego.
        config (dict)     : Diccionario de configuración del juego.
        chars (dict)      : Diccionario de caracteres y sus valores asociados.
    """
    global active_matches
    server_id = ctx.guild.id
        
    #Match load data
    # msg_game_start   = ""
    # msg_game_over    = random.choice(match.config["gameover"])
    # # msg_game_over2   = ""
    # # msg_tiempo_res   = ""
    
    #Match Welcome print
    await ctx.send(embed = Crear_Respuesta(f"{random.choice(match.config['startgame'])}" , f" {print_chars(match)}  \n{random.choice(match.config['startgame_2'])}, {essentials.num_to_emoji(match.cant_validas)} --- {random.choice(match.config['time_left'])} { essentials.num_to_emoji(tiempo_partida)}").enviar)
                        
    #Match Execution
    try:
        #Partida
        await asyncio.wait_for(match.get_inputs(ctx, bot), timeout=tiempo_partida)
    except asyncio.TimeoutError:
        #---ENDGAME---#
        server_id = await match.end(ctx)
        del active_matches[server_id] # Remover el id del servidor y la partida
        
        # palabras_mas_largas = essentials.seleccionar_palabras_mas_largas(match.palabras_posibles, top_palabras)
        # print(palabras_mas_largas)
        # match.active_match = False
        # active_matches[server_id] = False
        # #----Imprimir lista de jugadores----#
        # if not match.players:
        #     await ctx.send(embed = Crear_Respuesta(f'{random.choice(match.config["noplayers"])}' , None).enviar)
        # else:
        #     str_players = ""
        #     sorted_players = sorted(match.players, key=lambda x: x.points, reverse=True)
            
        #     for index, player in enumerate(sorted_players):
        #         if index < 3:
        #             medal = emoji_medals[index]
        #         else:
        #             medal = ""
                
        #         str_players += f"{medal} {player.name}: {essentials.num_to_emoji(player.points)} {random.choice(match.config['final_precomplement'])} - {essentials.num_to_emoji(player.words)} {random.choice(match.config['final_complement'])} \n"
        #     await ctx.send(embed = Crear_Respuesta( random.choice(match.config['players']) , f'{str_players}').enviar)
            
            
        # #----Imprimir palabras mas largas---#
        # if not palabras_mas_largas:
        #     await ctx.send(embed = Crear_Respuesta(f"Oops! Too unlucky ://" , None).enviar)
        # else:
        #     str_longers_w = ""
        #     for palabra in palabras_mas_largas:
        #         total_points = match.calcular_puntos(palabra)
        #         str_longers_w += f"**{palabra} -{essentials.num_to_emoji(total_points)}  {random.choice(match.config['final_precomplement'])}**  \n"
                
        #     await ctx.send(embed = Crear_Respuesta(f"{top_palabras} {random.choice(match.config['gameover_larger_words'])}", f"{str_longers_w}").enviar)   

# async def get_inputs(ctx, match):
#     """ Obtiene entradas del usuario de manera asíncrona y realiza el procesamiento de puntos y mensajes.

#     Args:
#         correct (list)  : Lista de mensajes de respuesta correcta.
#         incorrect (list): Lista de mensajes de respuesta incorrecta.
#         repeated (list) : Lista de mensajes de respuesta para palabra repetida.
#     """
#     server_id = ctx.guild.id
#     while active_matches[server_id]:
#         total_points = 0
#         ban          = 0
#         lop          = asyncio.get_event_loop()
#         # global tiempo_contador
        
#         if tiempo_contador is None or tiempo_contador.done():
#             lop             = asyncio.get_event_loop()
#             tiempo_contador = lop.create_task(match.contador_asincronico(ctx))
        
#         try:
#             user_message = await asyncio.wait_for(get_input(ctx, match), timeout= tiempo_partida)
#             #obtener mensaje del usuario
#             user_word = user_message.content
#             #Contamos las palabras en la frase. Si sólo se trata de 1 palabra hacemos el proceso, sino lo ignoramos.
#             if len(user_word.split()) == 1:
                
#                 #Eliminar espacios, tildes y mayusculas de la frase
#                 user_word = essentials.sanitizar_frase(user_word)
                
#                 # Verificar si la palabra es válida y procesarla.
#                 if match.palabras_posibles.__contains__(user_word):
#                     if user_word not in match.palabras_repetidas:
#                         total_points = match.calcular_puntos(user_word)
#                         match.palabras_repetidas.add(user_word)
#                         match.palabras_dichas += 1
#                     else:
#                         ban = 2
#                 else:
#                     ban = 1
                
#             #Outputs para cada caso de        
#             if ban == 0:
#                 found_player = None
#                 for player in match.players:
#                     if player.name == user_message.author.name:
#                         found_player = player
#                         break
                
#                 if found_player:
#                     found_player.__addpoints__(total_points)
#                     await ctx.send(embed = Crear_Respuesta(None , f'{found_player.name} {random.choice(match.config["correct"])} + {essentials.num_to_emoji(total_points)}').enviar)
#                 else:
#                     await ctx.send(embed = Crear_Respuesta(None , 'Player not found').enviar)
#             elif ban == 1:
#                 await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(match.config['incorrect'])}").enviar)
#             elif ban == 2:
#                 await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(match.config['repeated'])}").enviar)
#         except asyncio.TimeoutError:
#             break

# async def get_input(ctx, match):
#     """
#     Obtiene una entrada del usuario de manera asíncrona.

#     Utiliza el bucle de eventos asyncio para ejecutar la función de entrada (input()) en un
#     executor en segundo plano, lo que permite que la operación de entrada no bloquee el bucle
#     de eventos principal.

#     Returns:
#         str: La cadena de entrada proporcionada por el usuario.
#     """
#     def check(message):
#         return len(message.content.split()) == 1 and message.channel == ctx.channel
#     try:
#         user_input = await bot.wait_for("message", check=check, timeout=tiempo_partida)  # Esperar 60 segundos
#         #obtener nombre de usuario
#         user_name  = user_input.author.name
        
#         if not any(player.name == user_name for player in match.players):
#             new_player = Player(user_name)
#             match.players.append(new_player)
        
#         return user_input
    
#     except asyncio.TimeoutError:
#         await ctx.send("Tiempo de espera agotado o entrada inválida.")

            


# async def contador_asincronico(ctx, match):
#     """
#     Esta función simula un contador asincrónico con avisos y mensajes durante una partida.

#     Parámetros:
#     hurry (list): Lista de mensajes de prisa.
#     remember (list): Lista de mensajes de recordatorio.
#     time_left (list): Lista de mensajes sobre el tiempo restante.
#     chars (str): Caracteres válidos.
#     msg_gamestart_2 (str): Mensaje de inicio de partida.
#     cant_validas (int): Cantidad de palabras válidas.
#     """
#     #tiempo
#     global tiempo_partida
#     global tiempo_aviso
#     tiempo_aviso_copia = tiempo_aviso
    
#     while match.time > 0:
#         await asyncio.sleep(1)
#         print(match.time)
#         match.time         -= 1
#         tiempo_aviso_copia -= 1
        
#         #Tiempo agotándose
#         if match.time == tiempo_acabando:
#             await ctx.send(embed = Crear_Respuesta(f"{random.choice(match.config['hurry'])} {random.choice(match.config['time_left'])} { essentials.essentials.(match.match_time) } s" , None).enviar)
            
#         #Aviso cada cierto tiempo
#         if tiempo_aviso_copia == 0:

#             await ctx.send(embed = Crear_Respuesta(f"{random.choice(match.config['remember'])}", f"{print_chars(match)} \n {random.choice(match.config['startgame_2'])} {essentials.num_to_emoji(match.cant_validas - match.palabras_dichas)} \n {random.choice(match.config['time_left'])} { essentials.num_to_emoji(match.time) } s").enviar)                        
#             tiempo_aviso_copia = tiempo_aviso        

#------------------------------------------------------------------------------------
# Funciones del programa
#------------------------------------------------------------------------------------

    


# def calcular_puntos(palabra):
#     """
#     Calcula los puntos de la palabra de acuerdo a la puntuación vigente.

#     Args:
#         palabra (str): Palabra a puntuar

#     Returns:
#         int : puntuación
#     """
#     total_points = 0
#     chars_palabra = [char for char in palabra]
#     for char in chars_palabra:
#         total_points += chars_listos.get(char, 0)
#     return total_points
#------------------------------------------------------------------------------------
#Inicio del programa
#------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()