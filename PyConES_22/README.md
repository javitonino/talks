# Home is where your Assistant is written in Python

Una charla sobre HomeAssistant y cómo extenderlo.

### aerisweather

Una integración de HomeAssistant para cargar la predicción meteorológica usando el [API de AerisWeather](https://www.aerisweather.com/support/docs/api/).

### mqtt_gpio.py

Una integración sencilla por MQTT que permite controlar un GPIO de una Raspberry Pi (u otra placa similar) desde HomeAssistant.

### appdaemon

Una alternativa en Python para programar automatizaciones.

Se puede instalar con pip:

```
sudo pip3 install appdaemon
```

Y, para ejecutarlo, basta con pasarle por parámetro el directorio con la config (`-c`) que, en este repo se llama `appdaemon`:

```
appdaemon -c appdaemon
```
