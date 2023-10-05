import requests
import json

# Definir la información de autenticación de la API de OpenAI
API_KEY = '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'  # Reemplaza 'tu_api_key_aqui' con tu clave de API de OpenAI
API_URL = 'https://api.openai.com/v1/chat/completions'

# Realizar la solicitud a la API de OpenAI
def solicitar_respuesta_openai(conversacion):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    data = {
        'model': 'gpt-4',
        'messages': conversacion
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        respuesta = response.json()['choices'][0]['message']['content']
        return respuesta
    else:
        print("Error al comunicarse con la API de OpenAI. Código de estado:", response.status_code)
        print(response.text)
        return None

# Consumir la API local de almacenamiento de verduras
url_local_api = 'http://192.168.1.13:4000/api/almacen'
try:
    response = requests.get(url_local_api)
    response.raise_for_status()  # Lanzar una excepción en caso de error HTTP
    verdura = response.json()
except requests.exceptions.RequestException as e:
    print("Error al comunicarse con la API local:", e)
    verdura = {}

# Definir los parámetros para la conversación con OpenAI
conversacion = [
    {"role": "system", "content": "Tú eres un asistente de chat de un sistema agropecuario y consumes datos de un API de datos abiertos, tu objetivo es devolver respuestas concretas sobre la siguiente data que te muestro a continuación, tienes esta data de inventario: " + json.dumps(verdura)},
    {"role": "user", "content": "Hola, ¿cuántas unidades de zanahoria de calidad Premium hay?"},
]

# Realizar la solicitud a la API de OpenAI y obtener la respuesta
respuesta_openai = solicitar_respuesta_openai(conversacion)

if respuesta_openai:
    print("Respuesta del modelo de OpenAI:", respuesta_openai)

