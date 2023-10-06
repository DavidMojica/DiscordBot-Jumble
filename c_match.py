import os, io, json, random, essentials
from ds_prints import Crear_Respuesta
class Match:
    def __init__(self, match_time, match_lang):
        self.active_match = False
        self.time   = match_time
        self.total_posible_words = None
        self.match_lang = match_lang
        #load
        self.config = ""
        
        #Pesos y probabilidades
        self.q_consonants     = {"min_consonants": 6, "max_consonants": 12} #Siempre tiene que haber una  diferencia de 6 
        self.q_vocals         = {"min_vocals": 2, "max_vocals": 5}          #Siempre tiene que haber una diferencia de 3
        # Jugadores
        self.players = []
        self.players_name = set()
        self.chars = None
        self.pesos_consonants   = [0.2, 0.3, 0.3, 0.1, 0.06, 0.03, 0.01]      #Siempre tiene que haber 6 pesos
        self.pesos_vocals       = [0.35,0.30,0.25,0.10]                       #Cantidad de vocales: 2: 35% 3: 30% 4: 25% 5: 10%
        self.pesos_duplicados   = [0.1, 0.20, 0.20, 0.20, 0.20, 0.1]          # Probabilidades para 0 duplicados, 1 duplicado 2 duplicados, 3dup, 4 dup y 5dup
        self.pesos_puntos_extra = [0.35, 0.25, 0.20, 0.15, 0.1, 0.05]         #puntos extra: 0->  35%, 1->25%, 2-> 20%, 3-> 15%, 4-> 10%, 5-> 5%
        self.palabras_repetidas = set()
        self.chars_listos       = {}
        self.chars_display      = []
        self.palabras_posibles  = []
        self.palabras_dichas    = 0
        self.time_left = 0
        
    def start(self):
        self.active_match = True
        
    def end(self):
        self.active_match = False
        self.clear_data()
        
    def clear_data(self):
        self.chars = {}
        
    def calcular_puntos(self,palabra):
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
            print("patch 1")
            with io.open(config, encoding="utf-8") as c:
                print("patch 2")
                self.config = json.load(c)
                load_message = random.choice(self.config["loading"])
                await ctx.send(embed=Crear_Respuesta(load_message, None).enviar)

                # Seleccionamos la cantidad de letras y de duplicados de la partida
                numero_consonants = random.choices(range(self.q_consonants["min_consonants"], self.q_consonants["max_consonants"] + 1), weights=self.pesos_consonants)[0]
                numero_vocals = random.choices(range(self.q_vocals["min_vocals"], self.q_vocals["max_vocals"] + 1), weights=self.pesos_vocals)[0]
                numero_duplicados = random.choices(range(6), weights=self.pesos_duplicados)[0]

                consonants = random.sample(self.config["consonants"], numero_consonants)
                vocals = random.sample(self.config["vocals"], numero_vocals)
                chars = consonants + vocals
                # Duplicar letras si es necesario
                for _ in range(numero_duplicados):
                    chars.append(random.choice(chars))
                chars = random.sample(chars, len(chars))  # Desordenar aleatoriamente el orden de los elementos del array
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
                            puntos_extra = random.choices(range(1, 7), weights=self.pesos_puntos_extra)[0]
                            puntos_extras_asignados[char] = puntos_extra

                        pair = {char: puntos_extra}
                        self.chars_display.append(pair)
                        self.chars_listos[char] = puntos_extra

        return "0"

                    
            
        