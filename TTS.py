#import asyncio
import random
import edge_tts as tts
import pandas as pd
from mutagen.mp3 import MP3



    


async def record(text, Title, path):
    voices_path = ('Python\\Reddit Scraper\\Voices.csv')
    VOICE = pd.read_csv(voices_path)
    VOICE = VOICE['Voice'].to_list()
    

    voice = random.choice(VOICE) #Uses a different voice per item (Title, comment, etc.)
    voices = await tts.VoicesManager.create()
    say = tts.Communicate(str(text), str(voice)) 
    await say.save(path + '\\' + Title + '.mp3')




    '''Voice = ['Microsoft Server Speech Text to Speech Voice (en-AU, WilliamNeural)',
    'Microsoft Server Speech Text to Speech Voice (en-CA, LiamNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-IE, ConnorNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-IE, EmilyNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-GB, RyanNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-GB, SoniaNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-GB, ThomasNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, AvaMultilingualNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, AndrewMultilingualNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, EmmaMultilingualNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, BrianMultilingualNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, AvaNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, AndrewNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, BrianNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, ChristopherNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, EricNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)', 
    'Microsoft Server Speech Text to Speech Voice (en-US, MichelleNeural)']

'''


def get_length(path):
    try:
        audio = MP3(path)
        length = audio.info.length
        return length
    except:
        print('Error finding location')
        return None
    