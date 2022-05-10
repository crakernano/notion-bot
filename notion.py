# -*- coding: utf-8 -*-
'''
Bot para telegram
'''

import requests, json, os

from datetime import date

from telegram import (ParseMode)
from telegram.ext import (Updater, CommandHandler)

DATABASE_ID  =  os.environ["DATABASE_ID"]
NOTION_TOKEN =  os.environ["NOTION_TOKEN"]
NOTION_URL   = 'https://api.notion.com/v1/databases/'


# [Opcional] Recomendable poner un log con los errores que apareceran por pantalla.
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def consultaNotion():

    
    database_url = NOTION_URL + DATABASE_ID + "/query"
    response = requests.post(database_url, headers={"Authorization": f"{NOTION_TOKEN}", "Notion-Version": "2021-08-16"})

    tareas = []

    if response.status_code != 200:
        tareas.append("Error: %s" % str(response.status_code) )

    else:
        consulta = response.json()
        for resultado in consulta["results"]:
            tareas.append(resultado["properties"]["Titulo"]["title"][0]["text"]["content"])

    return tareas

def start(update, context):
	''' START '''
	# Enviar un mensaje a un ID determinado.
	context.bot.send_message(update.message.chat_id, "Bienvenido", parse_mode=ParseMode.HTML)

def tareas(update, context):
    msg = "Lista de tareas"
    update.message.reply_text(msg)

    tareas = consultaNotion()
    for tarea in tareas:
        update.message.reply_text(tarea)

def tareasHoy(update, context):

    readUrl = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    today = date.today()

    msg = "Tareas de hoy: %s" % str(today)
    update.message.reply_text(msg)

    headers = {
    "Accept": "application/json",
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16"
    }
    

    
    payload = {
        'filter': {
            'and': [
            {
                    'property': 'Deadline',
                    'date': {
                        'equals': str(today)
                    }
                }
            ]
        }
    }
    res = requests.request("POST", readUrl, json=payload, headers=headers)

    if res.status_code != 200:
        update.message.reply_text("Error: %s" % str(res.status_code))

    consulta = res.json()

    for resultado in consulta["results"]:
        update.message.reply_text(resultado["properties"]["Titulo"]["title"][0]["text"]["content"])


def nuevaTarea(update, context):
    
    headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json"
    }

    text = update.message.text

    cortar = text.find(" ")
    longitud = len(text)
    text = text[cortar:longitud]    

    url = 'https://api.notion.com/v1/pages'

    payload = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "Titulo": {
                "title": [
                    {
                        "text": {
                            "content": text
                        }
                    }
                ]
            }
        }
    }
    data = json.dumps(payload)

    response = requests.request("POST", url, headers=headers, data=data)

    if(response.status_code == 200):
        respuesta = "Tarea guardada correctamente %s " % text
    else:
        respuesta = "Error al guardar la tarea %s" % str(response.status_code)


    update.message.reply_text(respuesta)

def main():
    TOKEN=os.environ["TELEGRAM_TOKEN"]
    updater=Updater(TOKEN, use_context=True)
    dp=updater.dispatcher

	# Eventos que activarán nuestro bot.
	# /comandos
    dp.add_handler(CommandHandler('start',	start))
    dp.add_handler(CommandHandler('tareas',	tareas))
    dp.add_handler(CommandHandler('hoy',	tareasHoy))
    dp.add_handler(CommandHandler('nueva',	nuevaTarea))
    
    dp.add_error_handler(error_callback)
    # Comienza el bot
    updater.start_polling()
    # Lo deja a la escucha. Evita que se detenga.
    updater.idle()

if __name__ == '__main__':
	print(('Start %s' % os.environ["APP_NAME"]))
	main()
