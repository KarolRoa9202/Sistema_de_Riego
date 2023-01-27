from machine import Pin,I2C,ADC  # LIBRERIAS PARA UTILIZAR LOS METODOS DE MAQUINA Y MODULOS
                                 # ADEMAS DE LOS CONVERSORES ANALOGO DIGITAL
                                 
import OLED #LIBRERIA OLED PARA UTILIZAR FUNCIONES DE EDICION Y POSICIONAMIENTO DE DATOS QUE
            # REQUIEREN MOSTRAR EN PANTALLA.
            
import time # SIRVE PARA MANIPULAR LOS TIEMPOS O INTERVALOS ENTRE LA MEDIDAS DE LOS SENSORES

import dht  # LIBRERIA PARA UTILIZAR FUNCIONES, METODOS Y LECTURAS EN EL SENSOR DE 
            # DEL AMBIENTE TEMPERATURA Y HUMEDAD
            
import utime # FUNCION PARA MANIPULAR TIEMPOS EN MILISEGUNDOS

import bluetooth  # LIBRERIA PARA UTILIZAR LAS FUNCIONES DE BLUETOOTH QUE OFRECE EL ESP32
                    # CON ESTA FUNCION SE HACE LA COMUNICACION PARA LA APLICACION Y VISUALIZACION
                    # DE DATOS
                    
from BLE import BLEUART # FUNCIONES DE LECTURA Y ESCRITURIA COMUNICACION VIA BLUETOOTH PARA LA
                        # INFORMACION QUE SE QUIERE MOSTRAR EN LA APLICACION

name='SISTEMA_RIEGO' # ASIGNACION DE NOMBRE PARA LA COMUNICACION BLUETOOTH
ble=bluetooth.BLE()  # CONEXION CON LAS LIBRERIAS 
uart=BLEUART(ble,name)

pinesI2C = I2C(-1,Pin(4),Pin(5)) # ASIGNACION DE PINES PARA LA PANTALLA OLED 
oled = OLED.SSD1306_I2C(128, 64, pinesI2C) # DESCRIBIR LA PANTALLA QUE SE VA A UTILIZAR 

#ASIGNACION DE PINES PARA LOS SENSORES QUE SE UTILIZARON:

sensor_dht=dht.DHT11(Pin(15))  # SENSOR TEMPERATURA Y HUMEDAD AMBIENTE
sensor_luz=ADC(Pin(33))         # SENSOR FOTORESISTIVO
sensor_suelo=ADC(Pin(2))        # SENSOR HIGROMETRO HUMEDAD DE SUELO
sensor_monoxido=ADC(Pin(25))     # SENSOR MEDIDOR DE MONOXIDO

# LEDS INDICATIVOS:

led_calor=Pin(12,Pin.OUT)  # LED VENTILADOR DE CALOR 
led_frio=Pin(13,Pin.OUT)  # LED VENTILADOR DE FRIO
led_bomba_agua=Pin(14,Pin.OUT) # LED BOMBA DE AGUA 
led_luces=Pin(32,Pin.OUT)     # LED DE LUCES 
alarma_monoxido=Pin(27,Pin.OUT)  # LED NIVEL MONOXIDO
 
def lecturas(): # SE CREA UNA FUNCION PARA LECTURAS Y CONDICIONES  EL PROGRAMA 
    
    sensor_luz.atten(ADC.ATTN_11DB) # FUNCION DE MEDICION PARA RANGOS DE 0V A 3.3V
    valor_luz=sensor_luz.read()     # UTILIZANDO LA CONVERSION ANALOGO DIGITAL SE TOMAN LECTURAS
                                    # DEL SENSOR 
    
    if valor_luz>3000:                    # SE DEFINEN LOS RANGOS PARA LOS CUALES SE DECIDE 
#         print("Luces encendidas...")    # ENCENDER LAS LUCES O APAGARLAS SEGUN LA LECTURA
        led_luces.on()
    else:
#         print("Luces apagadas...")
        led_luces.off()
    
    sensor_suelo.atten(ADC.ATTN_11DB)      # SE DEFINEN LOS RANGOS PARA LOS CUALES SE DECIDE
    valor_suelo=sensor_suelo.read()        # ENCENDER LA BOMBA DE AGUA DEPENDIENDO DE PARAMETROS
    led_bomba_agua.off()                   # ESTABLECIODOS NOS MOSTRARA SI EL SUELO ESTA SECO
                                           # HUMEDO O MOJADO EL LED INDICATIVO BOMBA DE AGUA
    if valor_suelo >=1750:                 # SOLO ENCENDERA CUANDO EL SUELO ESTE SECO
        print("suelo seco")
        led_bomba_agua.on()
    elif valor_suelo<1750 and valor_suelo>=1430:
        print("suelo humedo")
        led_bomba_agua.off() 
    elif valor_suelo <1430:
        print("suelo mojado")
        led_bomba_agua.off()
        
        
    sensor_monoxido.atten(ADC.ATTN_11DB)     # SE DEFINEN LOS RANGOS PARA LOS CUALES SE DECIDE
    valor_monoxido=sensor_monoxido.read()   # ENCENDER LED INDICATIVO DEPENDIENDO DE PARAMETROS
    if valor_monoxido<=2860:                # DE MONOXIDO SI EXISTEN ALTOS NIVELES SE APAGARA
        alarma_monoxido.on()
#         print(valor_monoxido)
    elif valor_monoxido>2860:
        alarma_monoxido.off()
#         print(valor_monoxido)
    
    sensor_dht.measure()                            #SE TOMAN LECTURAS DEL SENSOR 
    temperatura_ambiente = sensor_dht.temperature() #SE TOMAN LECTURAS DE TEMPERATURA 
    humedad_ambiente = sensor_dht.humidity()        #SE TOMAN LECTURAS DE HUMEDAD
    led_frio.off()                                  #SE INICIALIZAN LOS VALOREN EN 0(APAGADOS)
    led_calor.off()
    
    if temperatura_ambiente>26 and temperatura_ambiente<=29: 
#         print("ventilador de frio encendido...")          #PARA VALORES ENTRE 27 Y 29 GRADOS
        led_frio.on()
        led_calor.off()                                      # ENCENDERA EL VENTILADOR DE FRIO
    elif temperatura_ambiente<=20:
#         print("ventilador de calor encendido...")   # PARA VALORES MENORES A 20 ENCEDERA EL
        led_calor.on()                                # VENTILADOR DE CALOR CON ESO SE MANTIENE 
        led_frio.off()                                # UNA TEMPERATURA ENTRE 21 Y 26 GRADOS
                                                      # SE PUEDE ADECUAR DIFERENTES RANGOS 
        
    oled.fill(0)#LIMPIA INICIALMETE LA PANTALLA
    oled.text("TEMPERATURA:",0,0)
    oled.text(str(temperatura_ambiente),95,0)
    oled.text("C",115,0)
    oled.text("HUM-AMBIENTE:",0,10)
    oled.text(str(humedad_ambiente),105,10)    # SE MUESTRAN LOS DATOS DE LAS CORRESPONDIENTES
    oled.text("%",120,10)                      # MEDIDAS DE CADA SENSOR DEFINIENDO LAS POSICIONES
    oled.text("LUMINOSIDAD:",0,20)             # EN LA PANTALLA OLED
    oled.text(str(valor_luz),95,20)
    oled.text("HUM-SUELO:",0,30)
    oled.text(str(valor_suelo),95,30)
    oled.text("NIVEL",0,40)
    oled.text("MONOXIDO:",0,50)
    oled.text(str(valor_monoxido),95,50)
    oled.show()# PERMITE VISUALIZAR LOS DATOS ENVIADOS 
    
    buffer=uart.read().decode().strip() # LECTURA DEL BUFFER ,DECODIFICACION DE LA INFORMACION
                                     # BARRIDO DE INFORMACION PARA LA COMUNICACION INALAMBRICA
                                        
     # VISUALIZACION DATOS DE LOS SENSORES EN LA APLICACION CONEXION INALAMBRICA
     
    uart.write('\n'+'------DATOS------'+'\n'+'TEPERATURA:'+str(temperatura_ambiente)+'_C'
               +'\n'+'HUMEDAD-AMBIENTE:'+str(humedad_ambiente)+'_%'
               +'\n'+'LUMINOSIDAD:'+str(valor_luz)                   
               +'\n'+'HUMEDAD-SUELO:'+str(valor_suelo)
               +'\n'+'NIVEL-MONOXIDO:'+str(valor_monoxido)+'\n')
    
    
intervalos_medidas= 2000 # DEFINIMOS EL VALOR DE CADA MEDIDAD DE LOS SENSORES 
comienzo=time.ticks_ms() # PARA UNA LECTURA MAS PRECISA

# CICLO DE EJECUCION DEL PROGRAMA CONTINUO 
while True:
    if time.ticks_ms() - comienzo >= intervalos_medidas:
        lecturas()

    
