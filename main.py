import os
import google.generativeai as genai
import requests
from twitchio.ext import commands

# Configurazioni
TWITCH_TOKEN = "3a25q0apz8638r1dtf09c8fawyt922"  # Sostituisci con il tuo token Twitch
TWITCH_CLIENT_ID = "59h009bh1qf25c5aog8cj2g8kjgq4r"  # Il tuo Client ID
TWITCH_PREFIX = "!"  # Prefisso per i comandi
GEMINI_API_KEY = "AIzaSyCuUsoZ1mqXtVJVrAmi9QX1OZowAh6dIdE"  # Chiave API di Gemini
GOOGLE_API_KEY = "AIzaSyCuUsoZ1mqXtVJVrAmi9QX1OZowAh6dIdE"  # Chiave API di Google Custom Search
GOOGLE_CSE_ID = "e154477fcd0ce4192"  # ID del motore di ricerca personalizzato

# Filtri per parole e temi vietati
BANNED_WORDS = {"bestemmia1", "bestemmia2", "parolaccia1", "parolaccia2"}
BANNED_TOPICS = {"morte", "omicidio", "politica", "uccidere", "suicidio", "violenza"}

# Configura Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')  # Usa il modello Gemini Pro

class ByteWritter(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            prefix=TWITCH_PREFIX,
            initial_channels=["trinityXpodcast"]  # Sostituisci con il tuo canale
        )

    async def event_ready(self):
        print(f"ByteWritter è pronto! Connesso come {self.nick}")
        print(f"Canali connessi: {self.connected_channels}")  # Debug

    async def event_message(self, message):
        if message.author is None:  # Ignora messaggi senza autore (messaggi di sistema)
            return

        print(f"Messaggio ricevuto da {message.author.name}: {message.content}")  # Debug
        if message.author.name.lower() == self.nick.lower():
            return  # Ignora i messaggi dell'IA stessa

        if message.content.startswith("@bytewritter"):
            print(f"Elaborazione del messaggio: {message.content}")  # Debug
            await self.handle_message(message)

    async def handle_message(self, message):
        content = message.content.lower()
        prompt = content[len("@bytewritter"):].strip()

        if self.is_content_inappropriate(prompt):
            await message.channel.send("Mi dispiace, non posso discutere di questo argomento.")
            return

        # Verifica se il messaggio richiede una ricerca su Google
        if "cerca su google" in prompt or "notizie su" in prompt:
            query = prompt.replace("cerca su google", "").replace("notizie su", "").strip()
            search_results = self.search_google(query)
            if search_results:
                response = self.generate_response_with_gemini(f"Riassumi queste informazioni: {search_results}")
            else:
                response = "Nessun risultato trovato su Google."
        else:
            response = self.generate_response_with_gemini(prompt)

        print(f"Risposta generata: {response}")  # Debug

        # Invia la risposta in blocchi di 500 caratteri
        for chunk in self.split_text(response, 500):
            await message.channel.send(chunk)

    def is_content_inappropriate(self, content):
        for word in BANNED_WORDS:
            if word in content:
                return True
        for topic in BANNED_TOPICS:
            if topic in content:
                return True
        return False

    def generate_response_with_gemini(self, prompt):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Errore durante la generazione della risposta: {e}")  # Debug
            return f"Errore durante la generazione della risposta: {e}"

    def search_google(self, query):
        """Esegue una ricerca su Google e restituisce i risultati."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 3  # Numero di risultati da restituire
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("items", [])
            if results:
                return "\n".join([result["snippet"] for result in results])
            else:
                return None
        except Exception as e:
            print(f"Errore durante la ricerca su Google: {e}")  # Debug
            return None

    def split_text(self, text, max_length):
        """Divide il testo in blocchi di lunghezza massima specificata."""
        for i in range(0, len(text), max_length):
            yield text[i:i + max_length]

if __name__ == "__main__":
    bot = ByteWritter()
    try:
        bot.run()
    except Exception as e:
        print(f"Errore durante l'esecuzione del bot: {e}")