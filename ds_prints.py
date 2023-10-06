import discord
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