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
#            Release version: 1.2 - 7/10/23 (saturday)          #
#***************************************************************#
#------------------------------------------------------------------------------------
#Imports
#------------------------------------------------------------------------------------
import unicodedata
#Emojis
emoji_medals  = ["🥇", " 🥈 ", " 🥉"]
emoji_numbers = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]

def num_to_emoji(num):
    """Convierte un numero a carácteres emoji """
    return ' '.join(emoji_numbers[int(n)] for n in str(num))

def print_chars(match):
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
    for index, dicts in enumerate(match.chars_display, start=1):
        for char, puntos in dicts.items():
            string_chars += f" **{char} - **{emoji_numbers[puntos]}"
           
            if index % 4 == 0:
                string_chars += "\n"
    return string_chars

def puede_formarse(palabra, cadena):
    """
    Comprueba si todos los caracteres de una palabra pueden formarse con los caracteres dados en una cadena.

    Esta función toma una palabra y una cadena de caracteres como entrada, luego crea conjuntos (sets) de los caracteres
    en la palabra y en la cadena. Finalmente, utiliza el método issubset() para verificar si el conjunto de caracteres
    de la palabra es un subconjunto del conjunto de caracteres de la cadena.

    Args:
        palabra (str): La palabra que se quiere comprobar si puede formarse con los caracteres de la cadena.
        cadena (str): Cadena de caracteres de la cual se quiere verificar la formación de la palabra.

    Returns:
        bool: True si todos los caracteres de la palabra pueden formarse con los caracteres de la cadena,
        False en caso contrario.
    """
    return set(palabra).issubset(set(cadena))
 
def actualizar_caracteres_usados(palabra, caracteres_usados):
    """
    Actualiza la lista de caracteres usados con base en una palabra dada.

    Esta función recorre cada caracter de la palabra y verifica si ya ha sido utilizado,
    eliminándolo de la lista de caracteres_usados si es el caso. Si encuentra un caracter
    que no está en la lista, devuelve False para indicar que el caracter no estaba en la lista
    original de caracteres_usados.

    Args:
        palabra (str): La palabra de la cual se van a actualizar los caracteres usados.
        caracteres_usados (list): Lista de caracteres utilizados que se va a actualizar.

    Returns:
        bool: True si todos los caracteres de la palabra ya existían en la lista y fueron
        removidos correctamente; False si al menos un caracter de la palabra no estaba en
        la lista original de caracteres_usados.
    """
    for caracter in palabra:
        if caracter in caracteres_usados:
            caracteres_usados.remove(caracter)
        else:
            return False
    return True

def compatibilidad(cadena, archivo):
    """
    Calcula la compatibilidad entre una cadena de caracteres y una lista de palabras en el archivo.

    Esta función recorre cada palabra en el archivo y verifica si puede formarse utilizando los caracteres
    presentes en la cadena dada. Si es posible formar la palabra, actualiza los caracteres usados en la cadena
    y agrega la palabra a una lista de palabras válidas. Al final, devuelve la cantidad total de palabras válidas
    y la lista de palabras válidas encontradas.

    Args:
        cadena (str): Cadena de caracteres con los que se intentarán formar las palabras.
        archivo (list): Lista de palabras en la que se verificará la compatibilidad.

    Returns:
        int  : Un número que nos indica la cantidad de palabras validas que el usuario puede encontrar.
        tuple: Una tupla que contiene la cantidad de palabras válidas encontradas y una lista con las palabras válidas.
    """
    cant_validas = 0
    lista_validas = []

    for palabra in archivo:
        if puede_formarse(palabra, cadena) and actualizar_caracteres_usados(palabra, list(cadena)):
            cant_validas += 1
            lista_validas.append(palabra)

    return cant_validas, lista_validas

def sanitizar_frase(frase):
    """ Realiza la sanitización de una frase, eliminando espacios en blanco adicionales, convirtiéndola a minúsculas
    y eliminando diacríticos.
    NFD: Unicode Forma Normalizada Descomposición, descompone los caracteres con diacríticos en una secuencia de caracteres base y marcas diacríticas.
    Mn : Categoria que corresponde a las marcas diacríticas

    Args:
        frase (str): La frase que se va a sanitizar.

    Returns:
        str: La frase sanitizada sin espacios en blanco adicionales, en minúsculas y sin diacríticos.
    """
    frase_sanitizada = frase.strip().lower()
    frase_sanitizada = ''.join(c for c in unicodedata.normalize('NFD', frase_sanitizada) if unicodedata.category(c) != 'Mn')
    return frase_sanitizada

def seleccionar_palabras_mas_largas(lista, numero_palabras):
    if not lista:
        return []
    
    sorted_lista = sorted(lista, key=len, reverse=True)
    return sorted_lista[:numero_palabras]

def tryParse(dato, tipo_dato):
    """
    Esta función intenta convertir el dato en el tipo de dato solicitado y devuelve el tipo de dato ya convertido si la conversion es exitosa, también devuelve True. En caso contrario, devuelve el dato sin convertir y False.
    
    Parámetros:
    dato (any)           : El dato que se quiere convertir.
    tipo_dato(data_type) : Tipo de dato al que se quiere convertir.
    
    Retorna: (any),(bool)
    (tipo_dato)Any, True : Si el elemento ha sido convertido con exito.
    Any, False           : Si el elemento no logró ser convertido.
    
    Ejemplo:
    nombre = "42asd"
    edad = "1000"
    
    >>>nombre, confirmation = tryParse(nombre, int)
    nombre: "42asd", confirmation = False
    
    >>>nombre, confirmation = tryParse(nombre, str)
    nombre = "42asd", confirmation = True
    
    >>>edad, confirmation = tryParse(edad, int)
    edad = 1000, confirmarion = True
    """
    try:
        return tipo_dato(dato), True
    except (ValueError, TypeError):
        return dato, False