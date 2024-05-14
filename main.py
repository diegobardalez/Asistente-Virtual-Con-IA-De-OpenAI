import pygame
import time
import os
import speech_recognition as sr
from openai import OpenAI
import tempfile
import threading
import pyaudio


client = OpenAI(
    api_key="API KEY AQUI!",
)

def reproducir_audio(nombre_archivo):
    pygame.mixer.init()
    pygame.mixer.music.load(nombre_archivo)
    pygame.mixer.music.play()

    # Establecer el volumen al máximo
    pygame.mixer.music.set_volume(1.0)

    # Esperar a que termine de reproducirse el audio
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # Cerrar el dispositivo de audio
    pygame.mixer.quit()

    # Eliminar el archivo de audio después de la reproducción
    try:
        os.remove(nombre_archivo)
    except PermissionError as e:
        print(f"No se pudo eliminar '{nombre_archivo}': {e}")



def texto_a_voz(texto):
    speech_file_path = "speech.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=texto
    )
    response.stream_to_file(speech_file_path)
    reproducir_audio(speech_file_path)


def consultar_gpt(texto):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": "Eres la asistente virtual llamada Luz creada por diego bardález plaza"}]},
            {"role": "user", "content": [{"type": "text", "text": texto}]}
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    respuesta = response.choices[0].message.content
    print(respuesta)
    texto_a_voz(respuesta)

def escuchar_microfono():
    reconocimiento = sr.Recognizer()
    # Obtener el ID del micrófono por defecto
    mic_id = sr.Microphone().list_microphone_names().index("CABLE Output (VB-Audio Point)")
    print(mic_id)

    while True:
        with sr.Microphone() as source:
            print(source)
            print("Di algo...")
            audio = reconocimiento.listen(source)
            try:
                print("Reconociendo...")
                texto = reconocimiento.recognize_google(audio, language="es-ES")
                print("Has dicho:", texto)
                if texto.lower().startswith("luz"):
                    consultar_gpt(texto[len("luz"):].strip())
                else:
                    print("No se activó la asistente virtual.")
            except sr.UnknownValueError:
                print("No se pudo entender lo que dijiste")
                #texto_a_voz("No se pudo entender lo que dijiste")
            except sr.RequestError as e:
                print("Error al solicitar resultados del servicio de reconocimiento de voz; {0}".format(e))
        # Agregar un pequeño retraso para permitir que el micrófono se estabilice
        time.sleep(0.5)

def listar_microfonos():
    p = pyaudio.PyAudio()
    num_dispositivos = p.get_device_count()
    
    print("Listado de dispositivos de entrada de audio:")
    for i in range(num_dispositivos):
        dispositivo_info = p.get_device_info_by_index(i)
        if dispositivo_info.get('maxInputChannels') > 0:
            print(f"ID: {i}, Nombre: {dispositivo_info.get('name')}")

# Iniciar la función para escuchar continuamente en un hilo separado para no bloquear el programa principal
threading.Thread(target=escuchar_microfono).start()
#listar_microfonos();
