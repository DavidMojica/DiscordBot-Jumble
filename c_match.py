import os
import io
import json
import random
import asyncio
import essentials
from c_player import Player
from ds_prints import Crear_Respuesta
# from Jumble import active_matches, bot


class Match:
    def __init__(self, match_time, match_lang):
        self.active_match = True
        self.time = match_time
        self.time_copy = match_time
        self.total_posible_words = None
        self.match_lang = match_lang
        #adverts
        self.time_going_out = 20
        self.time_advert = 5  # Tiempre entre cada aviso
        # load
        self.config = ""

        # Pesos y probabilidades
        # Siempre tiene que haber una  diferencia de 6
        self.q_consonants = {"min_consonants": 6, "max_consonants": 12}
        # Siempre tiene que haber una diferencia de 3
        self.q_vocals = {"min_vocals": 2, "max_vocals": 5}
        # Jugadores
        self.players = []
        self.players_name = set()
        self.chars = None
        
        #words
        self.cant_validas = 0
        self.top_palabras = 15
        # Siempre tiene que haber 6 pesos
        self.pesos_consonants = [0.2, 0.3, 0.3, 0.1, 0.06, 0.03, 0.01]
        # Cantidad de vocales: 2: 35% 3: 30% 4: 25% 5: 10%
        self.pesos_vocals = [0.35, 0.30, 0.25, 0.10]
        # Probabilidades para 0 duplicados, 1 duplicado 2 duplicados, 3dup, 4 dup y 5dup
        self.pesos_duplicados = [0.1, 0.20, 0.20, 0.20, 0.20, 0.1]
        # puntos extra: 0->  35%, 1->25%, 2-> 20%, 3-> 15%, 4-> 10%, 5-> 5%
        self.pesos_puntos_extra = [0.35, 0.25, 0.20, 0.15, 0.1, 0.05]
        self.palabras_repetidas = set()
        self.chars_listos = {}
        self.chars_display = []
        self.palabras_posibles = []
        self.palabras_dichas = 0
        self.time_left = 0
        self.tiempo_contador = None
    
    async def get_input(self, ctx, bot):
        """
        Obtiene una entrada del usuario de manera asíncrona.

        Utiliza el bucle de eventos asyncio para ejecutar la función de entrada (input()) en un
        executor en segundo plano, lo que permite que la operación de entrada no bloquee el bucle
        de eventos principal.

        Returns:
            str: La cadena de entrada proporcionada por el usuario.
        """
        print("patch 3")
        def check(message):
            return len(message.content.split()) == 1 and message.channel == ctx.channel
        try:
            user_input = await bot.wait_for("message", check=check, timeout=self.time_copy)  # Esperar 60 segundos
            #obtener nombre de usuario
            user_name  = user_input.author.name
            
            if not any(player.name == user_name for player in self.players):
                new_player = Player(user_name)
                self.players.append(new_player)
            
            return user_input
        
        except asyncio.TimeoutError:
            await ctx.send("Tiempo de espera agotado o entrada inválida.")
               
    async def get_inputs(self, ctx, bot):
        print("patch 1")
        server_id = ctx.guild.id
        while self.active_match:
            print("patch 2")
            total_points = 0
            ban          = 0
            lop          = asyncio.get_event_loop()
            
            if self.tiempo_contador is None or self.tiempo_contador.done():
                lop          = asyncio.get_event_loop()
                self.tiempo_contador = lop.create_task(self.contador_asincronico(ctx))
                
            try:
                user_message = await asyncio.wait_for(self.get_input(ctx, bot), timeout= self.time_copy)
                user_word = user_message.content
                print("patch 4")
                if len(user_word.split()) == 1:
                    #Eliminar espacios, tildes y mayusculas de la frase
                    user_word = essentials.sanitizar_frase(user_word)
                    
                    # Verificar si la palabra es válida y procesarla.
                    if self.palabras_posibles.__contains__(user_word):
                        if user_word not in self.palabras_repetidas:
                            total_points = self.calcular_puntos(user_word)
                            self.palabras_repetidas.add(user_word)
                            self.palabras_dichas += 1
                        else:
                            ban = 2
                    else:
                        ban = 1
                
                #Outputs para cada caso de ban    
                if ban == 0:
                    found_player = None
                    for player in self.players:
                        if player.name == user_message.author.name:
                            found_player = player
                            break
                    
                    if found_player:
                        found_player.__addpoints__(total_points)
                        await ctx.send(embed = Crear_Respuesta(None , f'{found_player.name} {random.choice(self.config["correct"])} + {essentials.num_to_emoji(total_points)}').enviar)
                    else:
                        await ctx.send(embed = Crear_Respuesta(None , 'Player not found').enviar)
                elif ban == 1:
                    await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(self.config['incorrect'])}").enviar)
                elif ban == 2:
                    await ctx.send(embed = Crear_Respuesta(None, f"{random.choice(self.config['repeated'])}").enviar)
            
            except asyncio.TimeoutError:
                break

    async def contador_asincronico(self, ctx):
        try:
            time_advert_copy = self.time_advert
            serv_id = ctx.guild.id
            while self.time > 0:
                await asyncio.sleep(1)
                print(f"Server: {serv_id} time: {self.time}")
                self.time -= 1
                time_advert_copy -= 1
                
                #aviso cada cierto tiempo
                if time_advert_copy == 0 and self.time > 15:
                    await ctx.send(embed = Crear_Respuesta(f"{random.choice(self.config['remember'])}", f"{essentials.print_chars(self)} \n {random.choice(self.config['startgame_2'])} {essentials.num_to_emoji(self.cant_validas - self.palabras_dichas)} \n {random.choice(self.config['time_left'])} { essentials.num_to_emoji(self.time) } s").enviar)
                    time_advert_copy = self.time_advert
                
                #Tiempo agotándose
                if self.time == self.time_going_out:
                        await ctx.send(embed = Crear_Respuesta(f"{random.choice(self.config['hurry'])} {random.choice(self.config['time_left'])} { essentials.num_to_emoji(self.time) } s" , None).enviar)
        
        except Exception as e:
            print(f"excepcion: {str(e)}")
            
    async def start(self, ctx):
        #Match Welcome print
        await ctx.send(embed = Crear_Respuesta(f"{random.choice(self.config['startgame'])}" , f" {essentials.print_chars(self)}  \n{random.choice(self.config['startgame_2'])}, {essentials.num_to_emoji(self.cant_validas)} --- {random.choice(self.config['time_left'])} { essentials.num_to_emoji(self.time)}").enviar)
        

    async def end(self, ctx):
        server_id = ctx.guild.id
        print("end")
        palabras_mas_largas = essentials.seleccionar_palabras_mas_largas(self.palabras_posibles, self.top_palabras)
        print(palabras_mas_largas)
        self.active_match = False
        self.clear_data()
        
        if not self.players:
            await ctx.send(embed = Crear_Respuesta(f'{random.choice(self.config["noplayers"])}' , None).enviar)
        else:
            str_players = ""
            sorted_players = sorted(self.players, key=lambda x: x.points, reverse=True)
            
            for index, player in enumerate(sorted_players):
                if index < 3:
                    medal = essentials.emoji_medals[index]
                else:
                    medal = ""
                
                str_players += f"{medal} {player.name}: {essentials.num_to_emoji(player.points)} {random.choice(self.config['final_precomplement'])} - {essentials.num_to_emoji(player.words)} {random.choice(self.config['final_complement'])} \n"
            await ctx.send(embed = Crear_Respuesta( random.choice(self.config['players']) , f'{str_players}').enviar)
        
        #----Imprimir palabras mas largas---#
        if not palabras_mas_largas:
            await ctx.send(embed = Crear_Respuesta(f"Oops! Too unlucky ://" , None).enviar)
        else:
            str_longers_w = ""
            for palabra in palabras_mas_largas:
                total_points = self.calcular_puntos(palabra)
                str_longers_w += f"**{palabra} -{essentials.num_to_emoji(total_points)}  {random.choice(self.config['final_precomplement'])}**  \n"
                
            await ctx.send(embed = Crear_Respuesta(f"{self.top_palabras} {random.choice(self.config['gameover_larger_words'])}", f"{str_longers_w}").enviar)   
        
        
        
        return server_id
        
    
    
    
    
    def clear_data(self):
        self.chars = {}

    def calcular_puntos(self, palabra):
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
            total_points += self.chars_listos.get(char, 0)
        return total_points

    async def load(self, ctx, lang):
        # Inicialización
        self.palabras_dichas = 0
        self.players_name.clear()
        self.chars_display.clear()
        self.players.clear()
        ban = True

        while ban:
            if lang == "0":
                return "2"
            elif lang == "1":
                file = "EN/package_EN.json"
                config = "EN/config_EN.json"
                ban = False
            elif lang == "2":
                file = "ES/package_ES.json"
                config = "ES/config_ES.json"
                ban = False
            else:
                return "7"

        if os.path.exists(config):
            with io.open(config, encoding="utf-8") as c:
                self.config = json.load(c)
                load_message = random.choice(self.config["loading"])
                await ctx.send(embed=Crear_Respuesta(load_message, None).enviar)

                # Seleccionamos la cantidad de letras y de duplicados de la partida
                numero_consonants = random.choices(range(
                    self.q_consonants["min_consonants"], self.q_consonants["max_consonants"] + 1), weights=self.pesos_consonants)[0]
                numero_vocals = random.choices(range(
                    self.q_vocals["min_vocals"], self.q_vocals["max_vocals"] + 1), weights=self.pesos_vocals)[0]
                numero_duplicados = random.choices(
                    range(6), weights=self.pesos_duplicados)[0]

                consonants = random.sample(
                    self.config["consonants"], numero_consonants)
                vocals = random.sample(self.config["vocals"], numero_vocals)
                chars = consonants + vocals
                # Duplicar letras si es necesario
                for _ in range(numero_duplicados):
                    chars.append(random.choice(chars))
                # Desordenar aleatoriamente el orden de los elementos del array
                chars = random.sample(chars, len(chars))
                print(chars)

                # Comprobar si el archivo de palabras existe.
                if os.path.exists(file):
                    with io.open(file, encoding="utf-8") as f:
                        jfile = json.load(f)
                        self.cant_validas, lista_validas = essentials.compatibilidad(chars, jfile)
                        print(self.cant_validas)
                        # Cargar la lista global de palabras posibles
                        self.palabras_posibles = lista_validas

                    # Otorgar puntuación a cada letra
                    puntos_extras_asignados = {}

                    for char in chars:
                        if char in puntos_extras_asignados:
                            # Reutilizar puntos extras para letras repetidas
                            puntos_extra = puntos_extras_asignados[char]
                        else:
                            # Asignar nuevos puntos extras a letras no repetidas
                            puntos_extra = random.choices(
                                range(1, 7), weights=self.pesos_puntos_extra)[0]
                            puntos_extras_asignados[char] = puntos_extra

                        pair = {char: puntos_extra}
                        self.chars_display.append(pair)
                        self.chars_listos[char] = puntos_extra

        return "0"
