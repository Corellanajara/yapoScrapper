import time
from bs4 import BeautifulSoup
import requests
import shutil
import urllib.request
import time
import mysql.connector as mysql
from PIL import Image
import pytesseract
import re
import datetime
from unicodedata import normalize


def ocr_core(filename):
    from PIL import Image
    import os, sys
    try:
        time.sleep(2)
        card = Image.new("RGBA", (220, 220), (255, 255, 255))
        img = Image.open(filename).convert("RGBA")
        x, y = img.size
        card.paste(img, (0, 0, x, y), img)
        card.save('mod/'+str(filename), format="png")
        text = pytesseract.image_to_string(Image.open('mod/'+str(filename)) )
        print(filename)
        return text

    except Exception as e:
        return "no se pudo obtener"

db = mysql.connect(
    host = "190.121.21.172",
    user = "unidadsi_yapo",
    #passwd = "claveyaposerver",
    passwd = "claveyaposerver",
    database="unidadsi_yapoAutos"
)


cantidadRegistros = 0
flag = True
url = 'https://www.yapo.cl/region_metropolitana/autos'
nPagina = 0;
an = 0;
fullDate = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
month = datetime.datetime.now().strftime("%m")
year = datetime.datetime.now().strftime("%Y")

while flag:
    nPagina = nPagina + 1
    sufijo = "?&o="+str(nPagina)
    response = requests.get(url+sufijo)
    soup = BeautifulSoup(response.text,'html.parser')
    anuncios = soup.find_all("tr", class_="ad listing_thumbs")

    for anuncio in anuncios:
            an = an + 1
            #print(an)
            datos = ""
            values = ""
            precio = ""
            urlVehiculo = anuncio.find("a",class_="redirect-to-url")
            urlAnuncio = urlVehiculo.get('href')
            peticion = requests.get(urlAnuncio)
            vehiculo = BeautifulSoup(peticion.text,'html.parser')

            sellerInfo = vehiculo.find('seller-info')

            nombreVendedor = sellerInfo.get('user-name')
            try:
                isPro = sellerInfo.getI('is-pro')
                #print(isPro)
            except Exception as e:
                isPro = "false"
                #print(e)

            seniority = sellerInfo.get('seniority')


            try:
                userStatus = vehiculo.find("div",class_="user-status")
                userStatus = userStatus.get_text()
            except Exception as e:
                #print(e)
                userStatus = "No tiene status definido"
            detalle = vehiculo.find("div",class_="details")
            body = detalle.find('tbody')
            #print(body)

            for tag in body:
                #print("------tag------")
                try:
                    th = tag.find("th")
                    th = th.get_text()
                    if(th == 'Código'):
                        td = tag.find("td")
                        td = td.get_text()
                        file = str(td)+'.png'
                        image_url = sellerInfo.get('phone-url')
                        resp = requests.get('https://www.yapo.cl'+str(image_url), stream=True)

                        with open(file, 'wb') as f:
                            f.write(resp.content)
                        with open(file, 'rb') as f:
                            r = requests.post('http://www.unidadsistemas.cl/yapo/recepcion.php', files={file: f})
                            print(r.text)
                        import os
                        os.remove(file)
                        print("Eliminado archivo temporal")
                        #numero = ocr_core(file)
                        numero = "no se pudo obtener"

                    if(th != 'Precio'):
                        td = tag.find("td")
                        td = td.get_text()
                        td = td.replace("\t", "")
                        td = td.replace("\n", "")
                        s = th
                        s = re.sub(
                                r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1",
                                normalize( "NFD", s), 0, re.I
                            )

                        # -> NFC
                        th = normalize( 'NFC', s)
                        th = th.replace(" ","")
                        th = th.split("(")[0]
                        print( s )
                        datos += " , `"+str(th)+"` "
                        values += " , '"+str(td)+" ' "
                        #print(tag)
                except Exception as e:
                    pass
                    ##print("este no funciono")
                    ##print(e)

            #print(datos+" values ("+values+")")
            dia = anuncio.find("span",class_="date")
            dia = dia.get_text()

            if(dia!="Hoy"):
                flag = False

            try:
                precio = anuncio.find("span",class_="price")
                precio = precio.get_text()
                precio = precio.replace("\t", "")

                precio = precio.replace("\n", "")
            except Exception as e:
                precio = "No hay precio definido"

            hora = anuncio.find("span",class_="hour")
            hora = hora.get_text()
            titulo = anuncio.find("a",class_="title")
            titulo = titulo.get_text()
            region = anuncio.find("span",class_="region")
            region = region.get_text()
            try:
                comuna = anuncio.find("span",class_="commune")
                comuna = comuna.get_text()
            except Exception as e:
                #print(e)
                comuna = "No hay comuna definida"
            print(str(dia) + " a las " + str(hora) + " se publica : "+str(titulo)+ " en "+str(comuna)+" a "+ str(precio) )
            try:
                cursor = db.cursor()

                insert = "insert into anuncio (fechaejecucion,Year,Mes,numero,userStatus,nombreVendedor,region,Precio,hora,titulo,comuna"
                sql = str(insert)+" "+str(datos)+" ) values ('"+fullDate+"','"+year+"','"+month+"','"+str(numero)+"','"+str(isPro)+"','"+str(nombreVendedor)+"','"+str(region)+"','"+str(precio)+"','"+str(hora)+"','"+str(titulo)+"','"+str(comuna)+"' "+str(values)+" )"
                cursor.execute(sql)
                db.commit()
                cantidadRegistros = cantidadRegistros + 1
            except Exception as e:
                print("este vehiculo (codigo) esta repetido")
            print("\n")

r = requests.post('http://www.unidadsistemas.cl/yapo/sendNotification.php', data={'fecha':fullDate,'registros':cantidadRegistros,'correo': 'corellanajara@hotmail.com'})
print(r.text)
r = requests.post('http://www.unidadsistemas.cl/yapo/sendNotification.php', data={'fecha':fullDate,'registros':cantidadRegistros,'correo': 'christianfuenzalidat@gmail.com'})
print(r.text)

