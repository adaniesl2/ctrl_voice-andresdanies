import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

import paho.mqtt.client as paho
import time
import json
import cv2
import numpy as np
#from PIL import Image
from PIL import Image as Image, ImageOps as ImagOps
from keras.models import load_model

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="157.230.214.127"
port=1883
client1= paho.Client("ADANIES")
client1.on_message = on_message



st.title("Bienvenido a tu Casa Inteligente")
st.subheader("Control de Luces")

image = Image.open('voice_ctrl.jpg')

st.image(image, width=200)




st.write("Toca el Botón y habla ")

stt_button = Button(label=" Inicio ", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                            
        client1.connect(broker,port)  
        message =json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_ADANIES_topic", message)

    
    try:
        os.mkdir("temp")
    except:
        pass

# Cerradura

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

        

model = load_model('keras_model.h5')
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

st.title("Cerradura Inteligente")

img_file_buffer = st.camera_input("Toma una Foto")

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
   #To read image file buffer as a PIL Image:
    img = Image.open(img_file_buffer)

    newsize = (224, 224)
    img = img.resize(newsize)
    # To convert PIL Image to numpy array:
    img_array = np.array(img)

    # Normalize the image
    normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    print(prediction)
    if prediction[0][0]>0.5:
      st.header('Abriendo')
      client1.publish("PuertaAD","{'gesto': 'Abre'}",qos=0, retain=False)
      time.sleep(0.2)
    if prediction[0][1]>0.5:
      st.header('Cerrando')
      client1.publish("PuertaAD","{'gesto': 'Cierra'}",qos=0, retain=False)
      time.sleep(0.2)  
