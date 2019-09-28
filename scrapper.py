from bs4 import BeautifulSoup
import requests
import urllib.request
import time
import mysql.connector as mysql

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "789123",
    database="yapoAutos"
)

print(db)
flag = True
url = 'https://www.yapo.cl/region_metropolitana/autos'
nPagina = 0;
while flag:
    nPagina = nPagina + 1
    sufijo = "?&o="+str(nPagina)
    response = requests.get(url+sufijo)
    soup = BeautifulSoup(response.text,'html.parser')
    anuncios = soup.find_all("tr", class_="ad listing_thumbs")

    for anuncio in anuncios:
            datos = ""
            values = ""
            precio = ""
            urlVehiculo = anuncio.find("a",class_="redirect-to-url")
            urlAnuncio = urlVehiculo.get('href')
            peticion = requests.get(urlAnuncio)
            vehiculo = BeautifulSoup(peticion.text,'html.parser')
            detalle = vehiculo.find("div",class_="details")
            body = detalle.find('tbody')
            print(body)

            for tag in body:
                print("------tag------")
                try:
                    th = tag.find("th")
                    th = th.get_text()
                    if(th != 'Precio'):
                        td = tag.find("td")
                        td = td.get_text()
                        td = td.replace("\t", "")
                        td = td.replace("\n", "")
                        datos += " , `"+str(th)+"` "
                        values += " , '"+str(td)+" ' "
                        print(tag)
                except Exception as e:
                    pass
                    #print("este no funciono")
                    #print(e)

            print(datos+" values ("+values+")")
            dia = anuncio.find("span",class_="date")
            dia = dia.get_text()

            if(dia!="Hoy"):
                flag = False
                break

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
            try:
                comuna = anuncio.find("span",class_="commune")
                comuna = comuna.get_text()
            except Exception as e:
                print(e)
                comuna = "No hay comuna definida"
            print("####################")
            print(str(dia) + " a las " + str(hora) + " se publica : "+str(titulo)+ " en "+str(comuna)+" a "+ str(precio) )
            cursor = db.cursor()
            insert = "insert into anuncio (Precio,hora,titulo,comuna"
            sql = str(insert)+" "+str(datos)+" ) values ('"+str(precio)+"','"+str(hora)+"','"+str(titulo)+"','"+str(comuna)+"' "+str(values)+" )"
            #sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
            print(sql)
            cursor.execute(sql)
            db.commit()
            print("\n")
