from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters
from telebot import types
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup

from pytube import YouTube
from dotenv import load_dotenv
import asyncio
import re
import os
import mock
from ytPatch import patched_throttling_plan

load_dotenv()
API_TOKEN = os.environ["TOKEN_BOT"]
bot = AsyncTeleBot(API_TOKEN, state_storage=StateMemoryStorage())
msg_send = {}
user_id = {}

class MyStates(StatesGroup):
	youtube = State()

class isYoutubeLink(asyncio_filters.SimpleCustomFilter):
	key='is_youtube_link'

	@staticmethod
	async def check(message: types.Message):
		search = re.search("^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$", str(message.text))
		return bool(search)

@bot.message_handler(commands=['help', 'start'])
async def send_message(message):
	msg = await bot.send_message(message.chat.id, "Hola, soy un bot sin un objetivo, pero que puede hacer muchas cosas" +
						  " utiles, aquí la selección de cosas que puedo hacer:",reply_markup=genMarkup())

	# DELETE MESSAGE AND SAVE THEM
	if message.chat.id in msg_send: # VALIDAR SI EXISTEN CLAVES
		await bot.delete_message(message.chat.id, msg_send[message.chat.id])
		del msg_send[message.chat.id]

	msg_send[msg.chat.id] = msg.message_id
	user_id[message.chat.id] = message.from_user.id
	await bot.delete_message(message.chat.id, message.message_id)

def genMarkup():
	key = types.InlineKeyboardMarkup()
	bVideoFromYoutube = types.InlineKeyboardButton("Obtener video de youtube", callback_data="video_youtube")
	key.add(bVideoFromYoutube)
	return key

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
async def backMenu(call):
    msg = await bot.send_message(call.message.chat.id, "Estas son las cosas utiles que puedo hacer: ", reply_markup=genMarkup())
    
    #DELETE AND SAVE THEM
    lista = msg_send[call.message.chat.id]
    for msgs in lista:
        await bot.delete_message(call.message.chat.id, msgs)

    del msg_send[call.message.chat.id]
    msg_send[call.message.chat.id] = msg.message_id


#CALLBACKS
@bot.callback_query_handler(func=lambda call: call.data == "video_youtube")
async def callbackMenu(call):
	msg = await bot.send_message(call.message.chat.id, "Ingrese el enlace o URL del video: ")
	await bot.set_state(user_id[call.message.chat.id], MyStates.youtube, call.message.chat.id)

	# DELETE AND SAVE THEM
	await bot.delete_message(call.message.chat.id, msg_send[call.message.chat.id])
	del msg_send[call.message.chat.id]
	msg_send[call.message.chat.id] = msg.message_id

@bot.message_handler(state=MyStates.youtube, is_youtube_link=True)
async def videoFromYoutube(message):
    try:
        load = await bot.send_message(message.chat.id, "Cargando...")
        
        with mock.patch('pytube.cipher.get_throttling_plan', patched_throttling_plan):
            yt = YouTube(message.text)
            key = types.InlineKeyboardMarkup()

            # SELECT RESOLUTION
            for stream in yt.streams.filter(file_extension="mp4").order_by(attribute_name="type"):
                if stream.is_progressive or ((stream.type == "audio") and stream.abr == "128kbps"):
                    if stream.abr == "128kbps":
                        audio = types.InlineKeyboardButton("(Audio) 128kbps", callback_data=f"audio128|{message.text}")
                        key.add(audio)
                    elif stream.resolution == "144p":
                        video = types.InlineKeyboardButton("144p", url=stream.url)
                        key.add(video)
                    elif stream.resolution == "240p":
                        video = types.InlineKeyboardButton("240p", url=stream.url)
                        key.add(video)
                    elif stream.resolution == "480p":
                        video = types.InlineKeyboardButton("480p", url=stream.url)
                        key.add(video)
                    elif stream.resolution == "720p":
                        video = types.InlineKeyboardButton("720p", url=stream.url)
                        key.add(video)

        volver = types.InlineKeyboardButton("Volver", callback_data="back_menu")
        key.add(volver)
        video = await bot.send_message(message.chat.id, f"{yt.title}", reply_markup=key)
        await bot.delete_state(message.from_user.id, message.chat.id)

        # DELETE AND SAVE THEM
        await bot.delete_message(message.chat.id, msg_send[message.chat.id])
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, load.message_id)
        del msg_send[message.chat.id]
        msg_send[message.chat.id] = [video.message_id]

    except Exception as e:
        print(e)

# GET INFORMATION VIDEO OR URL FOR DOWNLOAD
# @bot.message_handler(state=MyStates.youtube, is_youtube_link=True)
# async def videoFromYoutube(message):
# 	try:
# 		load = await bot.send_message(message.chat.id, "Cargando...")
#          
# 		yt = YouTube(message.text)
# 		key = types.InlineKeyboardMarkup()
#
# 		# SELECT RESOLUTION
# 		for stream in yt.streams.filter(file_extension="mp4").order_by(attribute_name="type"):
# 			if stream.is_progressive or ((stream.type == "audio") and stream.abr == "128kbps"):
# 				if stream.abr == "128kbps":
# 					audio = types.InlineKeyboardButton("(Audio) 128kpbs", callback_data=f"audio128|{message.text}")
# 					key.add(audio)
# 				elif stream.resolution == "144p":
# 					resolution = types.InlineKeyboardButton("144p", url=stream.url)
# 					key.add(resolution)
#
# 				elif stream.resolution == "240p":
# 					resolution = types.InlineKeyboardButton("240p", url=stream.url)
# 					key.add(resolution)
#
# 				elif stream.resolution == "360p":
# 					resolution = types.InlineKeyboardButton("360p", url=stream.url)
# 					key.add(resolution)
#
# 				elif stream.resolution == "480p":
# 					resolution = types.InlineKeyboardButton("480p", url=stream.url)
# 					key.add(resolution)
#
# 				elif stream.resolution == "720p":
# 					resolution = types.InlineKeyboardButton("720p", url=stream.url)
# 					key.add(resolution)
#
# 		volver = types.InlineKeyboardButton("Volver", callback_data="back_menu")
# 		key.add(volver)
# 		video = await bot.send_message(message.chat.id, f"{yt.title}", reply_markup=key)
# 		await bot.delete_state(message.from_user.id, message.chat.id)
#
# 		# DELETE AND SAVE THEM
# 		await bot.delete_message(message.chat.id, msg_send[message.chat.id])
# 		await bot.delete_message(message.chat.id, message.message_id)
# 		await bot.delete_message(message.chat.id, load.message_id)
# 		del msg_send[message.chat.id]
# 		msg_send[message.chat.id] = [video.message_id]
#
# 	except Exception as e:
# 		print("ha ocurrido un error -" + str(e))

@bot.message_handler(state=MyStates.youtube, is_youtube_link=False)
async def notVideoYotube(message):
	msg = await bot.reply_to(message, "Esta no es una URL de youtube, ingresa otra")

	# DELETE AND SAVE THEM
	await bot.delete_message(message.chat.id, msg_send[message.chat.id])
	await bot.delete_message(message.chat.id, message.message_id)
	del msg_send[message.chat.id]
	msg_send[message.chat.id] = msg.message_id

@bot.callback_query_handler(func=lambda call: call.data.split("|")[0] == "audio128")
async def getAudioFromVideo(call):
    try:
        load = await bot.send_message(call.message.chat.id, "Cargando...")
        
        with mock.patch('pytube.cipher.get_throttling_plan', patched_throttling_plan):
            yt = YouTube(call.data.split("|")[1])
            audio = yt.streams.filter(only_audio=True, abr="128kbps").first()
            path = os.path.join(os.getcwd(), "audios")
            out_file = audio.download(path) #type: ignore
            if not os.path.isfile(out_file.replace(".mp4", ".mp3")):
                os.rename(out_file, out_file.replace(".mp4", ".mp3"))
                with open(out_file.replace(".mp4", ".mp3"), "rb") as audio: 
                    audio = await bot.send_audio(call.message.chat.id, audio)
                    
                # SAVE AND DELETE MESSAGES
                msgs = msg_send[call.message.chat.id]
                msgs.append(audio.message_id)
                msg_send[call.message.chat.id] = msgs
                await bot.delete_message(call.message.chat.id, load.message_id)
            
            else:
                with open(out_file.replace(".mp4", ".mp3"), "rb") as audio:
                    audio = await bot.send_audio(call.message.chat.id, audio)

                # SAVE AND DELETE MESSAGES
                msgs = msg_send[call.message.chat.id]
                msgs.append(audio.message_id)
                msg_send[call.message.chat.id] = msgs
                await bot.delete_message(call.message.chat.id, load.message_id)

            os.remove(out_file.replace(".mp4", ".mp3"))

    except Exception as e:
        print(e)

# @bot.callback_query_handler(func=lambda call: call.data.split("|")[0] == "audio128")
# async def getAudioFromVideo(call):
#     try:
# 		# GET ONLY AUDIO
#         load = await bot.send_message(call.message.chat.id, "Cargando...")
#         yt = YouTube(call.data.split("|")[1])
#         audio = yt.streams.filter(only_audio=True, abr="128kbps").first()
#
# 		# DOWNLOAD, RENAME, SEND AND DELETE AUDIO
#         path = os.path.join(os.getcwd(), "audios")
#         out_file = audio.download(path) # type: ignore
#         if not os.path.isfile(out_file.replace(".mp4", ".mp3")):
#             os.rename(out_file, out_file.replace(".mp4", ".mp3"))
#             with open(out_file.replace(".mp4", ".mp3"), "rb") as audio:
#                 audio = await bot.send_audio(call.message.chat.id, audio)
#
# 				# SAVE AND DELETE MESSAGES
#                 msgs = msg_send[call.message.chat.id]
#                 msgs.append(audio.message_id)
#                 msg_send[call.message.chat.id] = msgs
#                 await bot.delete_message(call.message.chat.id, load.message_id)
#         else:
#             with open(out_file.replace(".mp4", ".mp3"), "rb") as audio:
#                 audio = await bot.send_audio(call.message.chat.id, audio)
#
# 				# SAVE AND DELETE MESSAGES
#                 msgs = msg_send[call.message.chat.id]
#                 msgs.append(audio.message_id)
#                 msg_send[call.message.chat.id] = msgs
#                 await bot.delete_message(call.message.chat.id, load.message_id)
#
#         os.remove(out_file.replace(".mp4", ".mp3"))
#     except Exception as e:



bot.add_custom_filter(isYoutubeLink())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))

asyncio.run(bot.polling())
