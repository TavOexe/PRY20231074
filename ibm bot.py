import requests

# Definir la información de autenticación
API_KEY = ''
API_URL = 'https://api.openai.com/v1/chat/completions'

#consumir api de verduras
url = ''
response = requests.get(url)
verdura = response.json()



# Definir los parámetros para la conversación
conversacion = [
    {"role": "system", "content": "Tú eres un asistente de chat de un sistema agropecuario y consumes datos de un API de datos abiertos. tienes esta data + ' verdura ' +  "},
    {"role": "user", "content": "codigo de tal producto"}
]

# Realizar la solicitud a la API
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

data = {
    'messages': conversacion
}

response = requests.post(API_URL, headers=headers, json=data)

if response.status_code == 200:
    respuesta = response.json()['choices'][0]['message']['content']
    print("Respuesta del modelo:", respuesta)
   
else:
    print("Error al comunicarse con la API. Código de estado:", response.status_code)
    print(response.text)



# Obtener la respuesta y mostrarla
print("Respuesta del API:", verdura)
