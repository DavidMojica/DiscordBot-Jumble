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
from c_player import Player
#------------------------------------------------------------------------------------
#Variables Globales
#------------------------------------------------------------------------------------
#---Bot---#
file_config_bot     = "config_bot/config_bot.json"
template_config_bot = {"prefix" : "%", "token": ""}
bot                 = None

#---Jumble---#
tiempo_partida   = 180
tiempo_partida_c = 180
tiempo_aviso     = 15  #Cada tiempo se le recordarán a los jugadores las letras que pueden usar y el tiempo que les queda.
tiempo_acabando  = 12
tiempo_contador  = None
file             = ""
config           = ""
consonants       = ""
vocals           = ""
q_consonants     = {"min_consonants": 6, "max_consonants": 12} #Siempre tiene que haber una  diferencia de 6 
q_vocals         = {"min_vocals": 2, "max_vocals": 5}          #Siempre tiene que haber una diferencia de 3
timeout_menu     = 10 #Expand
#Probabilities 
pesos_consonants   = [0.2, 0.3, 0.3, 0.1, 0.06, 0.03, 0.01]      #Siempre tiene que haber 6 pesos
pesos_vocals       = [0.35,0.30,0.25,0.10]                       #Cantidad de vocales: 2: 35% 3: 30% 4: 25% 5: 10%
pesos_duplicados   = [0.1, 0.20, 0.20, 0.20, 0.20, 0.1]          # Probabilidades para 0 duplicados, 1 duplicado 2 duplicados, 3dup, 4 dup y 5dup
pesos_puntos_extra = [0.35, 0.25, 0.20, 0.15, 0.1, 0.05]         #puntos extra: 0->  35%, 1->25%, 2-> 20%, 3-> 15%, 4-> 10%, 5-> 5%
#Active
active_match       = False
#Messages
top_palabras   = 15
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
#Emojis
emoji_numbers = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]
emoji_medals  = ["🥇", " 🥈 ", " 🥉"]

#Match variables
chars_listos       = {}
chars_display      = []
palabras_posibles  = []
palabras_dichas    = 0
palabras_repetidas = set()
nombre_jugadores   = set()

# Jugadores
players = []

#------------------------------------------------------------------------------------
#Clases
#------------------------------------------------------------------------------------
class Crear_Respuesta():
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.respuesta = discord.Embed(
            title = self.title,
            description=self.content,
            colour= int("FFFFFF",16)       
        )
    @property
    def enviar(self):
        return self.respuesta
    
    
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
        #     global active_match
        #     global tiempo_partida
            
        #     if active_match:
        #         msg_user = int(msg.content)
        #         tiempo_partida = msg_user
        #         await ctx.send(embed = Crear_Respuesta(f'{num_to_emoji(msg_6["head"])}s', msg_6["body"]).enviar)

        #     else:
        #         await ctx.send(embed = Crear_Respuesta(error_6["head"], error_6["body"]).enviar)

        @bot.command(name="reset", help="Restarts a jumble match.")
        async def reset(ctx):
            global active_match
            if active_match:
                await ctx.send(embed = Crear_Respuesta(msg_5["head"], msg_5["body"]).enviar)
                global tiempo_partida
                tiempo_partida = 0
                
                active_match = False
                await jumble(ctx)
            else:
                await ctx.send(embed = Crear_Respuesta(error_5["head"], error_5["body"]).enviar)


        
        @bot.command(name="stop", help="Stops a Jumble match")
        async def stop(ctx):
            global active_match
            if active_match:
                await ctx.send(embed = Crear_Respuesta(msg_4["head"], msg_4["body"]).enviar)
                global tiempo_partida
                tiempo_partida = 0
                
                active_match = False
            else:
                await ctx.send(embed = Crear_Respuesta(error_4["head"], error_4["body"]).enviar)

        
        @bot.command(name="jumble", help="Starts a Jumble match.")
        async def jumble(ctx):
            if not active_match:
                #Jumble reiniciar variables
                palabras_repetidas.clear()
                nombre_jugadores.clear()
                chars_display.clear()
                players.clear()
                
                global tiempo_partida
                tiempo_partida = tiempo_partida_c
                
                global cant_validas
                cant_validas = 0
                
                global palabras_dichas
                palabras_dichas = 0 
                
                #--------------------------------------------------------------------------------
                #Menu
                #--------------------------------------------------------------------------------
                ban = True
                await ctx.send(embed = Crear_Respuesta(msg_menu["head"] , msg_menu["body"]).enviar)
                
                def check(message):
                    return message.author == ctx.author
                
                try:
                    lang = await bot.wait_for("message", check=check, timeout=timeout_menu)
                    lang = lang.content # acceder al valor del mensaje
                    while ban:
                        if lang == "0":
                            await ctx.send(embed = Crear_Respuesta(error_2["head"] , error_2["body"]).enviar)
                            return
                        elif lang == "1":
                            file   = "EN/package_EN.json"
                            config = "EN/config_EN.json"
                            ban  = False
                        elif(lang == "2"):
                            file   = "ES/package_ES.json"
                            config = "ES/config_ES.json"
                            ban  = False
                        else:
                            await ctx.send(embed = Crear_Respuesta(error_7["head"] , error_7["body"]).enviar)
                            return
                    #------------------------------------------------------------------------------------
                    #CARGA - archivos externos
                    #------------------------------------------------------------------------------------       
                    try:
                            if os.path.exists(config):
                                with io.open(config, encoding="utf-8") as c:
                                    config     = json.load(c)
                                    load_message = random.choice(config["loading"])
                                    await ctx.send(embed = Crear_Respuesta(load_message , None).enviar)          
                                    #seleccionamos la cantidad de letras y de duplicados de la partida 
                                    numero_consonants = random.choices(range(q_consonants["min_consonants"], q_consonants["max_consonants"] + 1), weights=pesos_consonants)[0]
                                    numero_vocals     = random.choices(range(q_vocals["min_vocals"], q_vocals["max_vocals"] + 1), weights=pesos_vocals)[0]
                                    numero_duplicados = random.choices(range(6), weights=pesos_duplicados)[0]
                        
                                    consonants   = random.sample(config["consonants"], numero_consonants)
                                    vocals       = random.sample(config["vocals"], numero_vocals)    
                                    chars        = consonants + vocals
                        
                                    #Duplicar letras si hay que duplicarlas
                                    for _ in range (numero_duplicados):
                                        chars.append(random.choice(chars))
                                    chars      = random.sample(chars, len(chars))   #Desordenar aleatoriamente el orden de los elementos del array

                                    #Comprueba si el archivo de palabras existe.
                                    if os.path.exists(file):
                                        with io.open(file, encoding="utf-8") as f:
                                            jfile = json.load(f)
                                            cant_validas, lista_validas = essentials.compatibilidad(chars,jfile)
                                            #Cargar la lista global de palabras posibles
                                            global palabras_posibles
                                            palabras_posibles = lista_validas
                                            
                                        #Otorgar puntuación a cada letra
                                        puntos_extras_asignados = {}
                                        
                                        for char in chars:
                                            if char in puntos_extras_asignados:
                                                # Reutilizar puntos extras para letras repetidas
                                                puntos_extra = puntos_extras_asignados[char]
                                            else:
                                                # Asignar nuevos puntos extras a letras no repetidas
                                                puntos_extra = random.choices(range(1, 7), weights=pesos_puntos_extra)[0]
                                                puntos_extras_asignados[char] = puntos_extra
                                            pair = {}
                                            pair[char] = puntos_extra
                                            chars_display.append(pair)
                                            chars_listos[char] = puntos_extra
                                        
                                        #Empezar el juego
                                        await __startgame__(ctx,cant_validas, config, chars_listos)
                        
                    except(Exception) as error:
                        print(f"{repr(error)} en segundo try")                   
                except asyncio.TimeoutError:
                    await ctx.send(embed = Crear_Respuesta(error_1["head"], error_1["body"]).enviar)
            else:
                await ctx.send(embed = Crear_Respuesta(error_3["head"], error_3["body"]).enviar)
                
        #Encender el bot
        bot.run(token)
    except (Exception) as error:
        print(repr(error))

#------------------------------------------------------------------------------------
#Match - Partida
#------------------------------------------------------------------------------------
async def __startgame__(ctx, cant_validas, config, chars):
    """Inicia el juego y maneja la ejecución y el flujo de mensajes.

    Args:
        cant_validas (int): Cantidad de palabras válidas disponibles para el juego.
        config (dict)     : Diccionario de configuración del juego.
        chars (dict)      : Diccionario de caracteres y sus valores asociados.
    """
    global active_match
    active_match = True
    #Match load data
    msg_game_start   = random.choice(config["startgame"])
    msg_game_start2  = random.choice(config["startgame_2"])
    msg_game_over    = random.choice(config["gameover"])
    msg_game_over2   = random.choice(config["gameover_larger_words"])
    msg_tiempo_res   = random.choice(config["time_left"])
    
    #Match Welcome print
    await ctx.send(embed = Crear_Respuesta(f"{msg_game_start}" , f" {print_chars()}  \n{msg_game_start2}, {num_to_emoji(cant_validas)} --- {msg_tiempo_res} { num_to_emoji(tiempo_partida)}").enviar)
                        
    #Match Execution
    try:
        #Partida
        await asyncio.wait_for(get_inputs(ctx, config["correct"], config["incorrect"], config["repeated"], config["hurry"], config["remember"], config["time_left"], chars, msg_game_start2, cant_validas), timeout=tiempo_partida)
        pass
    except asyncio.TimeoutError:
        #---ENDGAME---#
        palabras_mas_largas = essentials.seleccionar_palabras_mas_largas(palabras_posibles, top_palabras)
        print(palabras_mas_largas)
        active_match = False
        #----Imprimir lista de jugadores----#
        if not players:
            await ctx.send(embed = Crear_Respuesta(f'{random.choice(config["noplayers"])}' , None).enviar)
        else:
            str_players = ""
            sorted_players = sorted(players, key=lambda x: x.points, reverse=True)
            
            for index, player in enumerate(sorted_players):
                if index < 3:
                    medal = emoji_medals[index]
                else:
                    medal = ""
                
                str_players += f"{medal} {player.name}: {num_to_emoji(player.points)} {random.choice(config['final_precomplement'])} - {num_to_emoji(player.words)} {random.choice(config['final_complement'])} \n"
            await ctx.send(embed = Crear_Respuesta( random.choice(config['players']) , f'{str_players}').enviar)
            
            
        #----Imprimir palabras mas largas---#
        if not palabras_mas_largas:
            await ctx.send(embed = Crear_Respuesta(f"Oops! Too unlucky ://" , None).enviar)
        else:
            str_longers_w = ""
            for palabra in palabras_mas_largas:
                total_points = calcular_puntos(palabra)
                str_longers_w += f"**{palabra} -{num_to_emoji(total_points)}  {random.choice(config['final_precomplement'])}**  \n"
                
            await ctx.send(embed = Crear_Respuesta(f"{top_palabras} {msg_game_over2}", f"{str_longers_w}").enviar)   

async def get_inputs(ctx, correct, incorrect, repeated, hurry, remember, time_left, chars, msg_gamestart_2, cant_validas):
    """ Obtiene entradas del usuario de manera asíncrona y realiza el procesamiento de puntos y mensajes.

    Args:
        correct (list)  : Lista de mensajes de respuesta correcta.
        incorrect (list): Lista de mensajes de respuesta incorrecta.
        repeated (list) : Lista de mensajes de respuesta para palabra repetida.
    """
    while active_match:
        total_points = 0
        ban          = 0
        lop          = asyncio.get_event_loop()
        global tiempo_contador
        
        if tiempo_contador is None or tiempo_contador.done():
            lop             = asyncio.get_event_loop()
            tiempo_contador = lop.create_task(contador_asincronico(ctx, hurry, remember, time_left,msg_gamestart_2, cant_validas))
        
        try:
            user_message = await asyncio.wait_for(get_input(ctx), timeout= tiempo_partida)
            #obtener mensaje del usuario
            user_word = user_message.content
            #Contamos las palabras en la frase. Si sólo se trata de 1 palabra hacemos el proceso, sino lo ignoramos.
            if len(user_word.split()) == 1:
                
                #Eliminar espacios, tildes y mayusculas de la frase
                user_word = essentials.sanitizar_frase(user_word)
                
                # Verificar si la palabra es válida y procesarla.
                if palabras_posibles.__contains__(user_word):
                    if user_word not in palabras_repetidas:
                        total_points = calcular_puntos(user_word)
                        palabras_repetidas.add(user_word)
                        global palabras_dichas 
                        palabras_dichas += 1
                    else:
                        ban = 2
                else:
                    ban = 1
                
            #Outputs para cada caso de        
            if ban == 0:
                found_player = None
                for player in players:
                    if player.name == user_message.author.name:
                        found_player = player
                        break
                
                if found_player:
                    found_player.__addpoints__(total_points)
                    await ctx.send(embed = Crear_Respuesta(None , f'{found_player.name} {random.choice(correct)} + {num_to_emoji(total_points)} points').enviar)
                else:
                    await ctx.send(embed = Crear_Respuesta(None , 'Player not found').enviar)
            elif ban == 1:
                await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(incorrect)}").enviar)
            elif ban == 2:
                await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(repeated)}").enviar)
        except asyncio.TimeoutError:
            break

async def get_input(ctx):
    """
    Obtiene una entrada del usuario de manera asíncrona.

    Utiliza el bucle de eventos asyncio para ejecutar la función de entrada (input()) en un
    executor en segundo plano, lo que permite que la operación de entrada no bloquee el bucle
    de eventos principal.

    Returns:
        str: La cadena de entrada proporcionada por el usuario.
    """
    def check(message):
        return len(message.content.split()) == 1 and message.channel == ctx.channel
    try:
        user_input = await bot.wait_for("message", check=check, timeout=tiempo_partida)  # Esperar 60 segundos
        #obtener nombre de usuario
        user_name  = user_input.author.name
        
        if not any(player.name == user_name for player in players):
            new_player = Player(user_name)
            players.append(new_player)
        
        return user_input
    
    except asyncio.TimeoutError:
        await ctx.send("Tiempo de espera agotado o entrada inválida.")

            


async def contador_asincronico(ctx,hurry, remember, time_left, msg_gamestart_2, cant_validas):
    """
    Esta función simula un contador asincrónico con avisos y mensajes durante una partida.

    Parámetros:
    hurry (list): Lista de mensajes de prisa.
    remember (list): Lista de mensajes de recordatorio.
    time_left (list): Lista de mensajes sobre el tiempo restante.
    chars (str): Caracteres válidos.
    msg_gamestart_2 (str): Mensaje de inicio de partida.
    cant_validas (int): Cantidad de palabras válidas.
    """
    #tiempo
    global tiempo_partida
    global tiempo_aviso
    tiempo_aviso_copia = tiempo_aviso
    
    while tiempo_partida > 0:
        await asyncio.sleep(1)
        tiempo_partida     -= 1
        tiempo_aviso_copia -= 1
        
        #Tiempo agotándose
        if tiempo_partida == tiempo_acabando:
            await ctx.send(embed = Crear_Respuesta(f"{random.choice(hurry)} {random.choice(time_left)} { num_to_emoji(tiempo_partida) } s" , None).enviar)
            
        #Aviso cada cierto tiempo
        if tiempo_aviso_copia == 0:
            
            await ctx.send(embed = Crear_Respuesta(f"{random.choice(remember)}", f"{print_chars()} \n {msg_gamestart_2} {num_to_emoji(cant_validas - palabras_dichas)} \n {random.choice(time_left)} { num_to_emoji(tiempo_partida) } s").enviar)                        
            tiempo_aviso_copia = tiempo_aviso        

#------------------------------------------------------------------------------------
# Funciones del programa
#------------------------------------------------------------------------------------
def print_chars():
    """ 
    Imprime los caracteres y sus puntos extras en forma de lista de diccionarios.

    Esta función toma como entrada un mensaje (msg) y la cantidad de palabras válidas (cant_validas) que el usuario puede encontrar.
    Luego recorre la lista de diccionarios chars_display, que contiene los caracteres y sus respectivos puntos extras,
    y los imprime en un formato legible.

    Args:
        msg (str): Mensaje que se imprimirá junto a la cantidad de palabras válidas.
        cant_validas (int): Cantidad de palabras válidas que el usuario puede encontrar.

    Returns:
        None: Esta función no devuelve ningún valor; simplemente imprime la información formateada.
    """
    string_chars = ""
    for index, dicts in enumerate(chars_display, start=1):
        for char, puntos in dicts.items():
            string_chars += f" **{char} - **{emoji_numbers[puntos]}"
           
            if index % 4 == 0:
                string_chars += "\n"
            
    return string_chars
    
def num_to_emoji(num):
    """
    Convierte un numero a carácteres emoji

    Args:
        num (int): el numero a ser transformado

    Returns:
        emoji: El numero en emoji
    """
    return ' '.join(emoji_numbers[int(n)] for n in str(num))

def calcular_puntos(palabra):
    """
    Calcula los puntos de la palabra de acuerdo a la puntuación vigente.

    Args:
        palabra (str): Palabra a puntuar

    Returns:
        int : puntuación
    """
    total_points = 0
    chars_palabra = [char for char in palabra]
    for char in chars_palabra:
        total_points += chars_listos.get(char, 0)
    return total_points
#------------------------------------------------------------------------------------
#Inicio del programa
#------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()