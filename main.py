import requests
import urllib.parse
import folium
import polyline

route_url = "https://graphhopper.com/api/1/route?"
key = "8207ef40-e417-47f4-9228-297c5a74f737"

def geocoding(location, key):
    while location == "":
        location = input("Ingrese la ubicación nuevamente: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key})

    replydata = requests.get(url)
    json_status = replydata.status_code
    json_data = replydata.json()

    if json_status == 200 and len(json_data["hits"]) != 0:
        # Extracción de coordenadas y detalles de la ubicación
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        # Construcción de la ubicación formateada con estado y país si están disponibles
        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif state:
            new_loc = f"{name}, {country}"
        else:
            new_loc = name

        # Impresión de la URL de la API de geocodificación y detalles relevantes
        print(f"\nGeocoding API URL for {new_loc} (Location Type: {value})\n{url}")
    else:
        # Manejo de casos donde la ubicación no se encuentra o hay errores en la respuesta
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            print(f"Estado de la API de Geocodificación: {json_status}\nMensaje de error: {json_data.get('message', 'No se encontró mensaje de error')}")

    return json_status, lat, lng, new_loc

def crear_mapa(origen, destino, coordenadas_ruta):
    # Creación de un mapa centrado en el punto medio entre origen y destino
    mapa = folium.Map(location=[(origen[1] + destino[1]) / 2, (origen[2] + destino[2]) / 2], zoom_start=13)
    
    # Marcadores para origen y destino en el mapa
    folium.Marker([origen[1], origen[2]], popup=origen[3], tooltip='Inicio').add_to(mapa)
    folium.Marker([destino[1], destino[2]], popup=destino[3], tooltip='Destino').add_to(mapa)

    # Línea de ruta en el mapa usando coordenadas de la ruta
    folium.PolyLine(coordenadas_ruta, color='blue', weight=2.5, opacity=1).add_to(mapa)
    
    # Guardar el mapa generado como archivo HTML y mostrar mensaje de confirmación
    mapa.save('ruta.html')
    print("\n***Archivo del mapa generado: ruta.html. Puedes revisarlo ahora.***\n")
    print("                       Fin del Programa\n")

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículos disponibles en Graphhopper:\n")
    print("Lista: car, bike, foot\n")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    perfiles = ["car", "bike", "foot"]
    vehiculo = input("Ingrese un perfil de vehículo de la lista anterior: ").strip().lower()
    if vehiculo == "quit" or vehiculo == "q":
        break
    elif vehiculo in perfiles:
        pass
    else:
        # Si no se ingresa un perfil válido, se usa el perfil de vehículo por defecto ("car")
        vehiculo = "car"
        print("No se ingresó un perfil de vehículo válido. Usando el perfil de car.\n")
    print("\n=================================================")
    loc1 = input("\nUbicación de inicio: ").strip()
    if loc1 == "quit" or loc1 == "q":
        break
    orig = geocoding(loc1, key)

    loc2 = input("\nDestino: ").strip()
    if loc2 == "quit" or loc2 == "q":
        break
    dest = geocoding(loc2, key)

    print("\n=================================================")
    if orig[0] == 200 and dest[0] == 200:
        # Construcción de la URL de la API de enrutamiento y obtención de datos de la ruta
        op = f"&point={orig[1]},{orig[2]}"
        dp = f"&point={dest[1]},{dest[2]}"
        paths_url = f"{route_url}key={key}&vehicle={vehiculo}{op}{dp}"
        paths_response = requests.get(paths_url)
        paths_data = paths_response.json()
        paths_status = paths_response.status_code

        # Impresión del estado y URL de la API de enrutamiento
        print(f"\nEstado de la API de Enrutamiento: {paths_status}")
        print(f"URL de la API de Enrutamiento:\n{paths_url}")
        print("\n=================================================")
        print(f"\nDirecciones desde {orig[3]} hasta {dest[3]} en {vehiculo}")
        print("\n=================================================")

        if paths_status == 200:
            try:
                # Extracción de detalles de la ruta: distancia, tiempo y pasos de instrucción
                km = paths_data["paths"][0]["distance"] / 1000
                sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
                min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
                hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
                print(f"\nDistancia recorrida: {km:.1f} km")
                print(f"Duración del viaje: {hr:02}:{min:02}:{sec:02}")
                print("\n=================================================")

                for instruction in paths_data["paths"][0]["instructions"]:
                    # Iteración sobre las instrucciones de la ruta y sus distancias
                    camino = instruction["text"]
                    distancia = instruction["distance"]
                    print(f"{camino} ( {distancia / 1000:.1f} km )")

                print("=============================================")

                # Decodificación de puntos codificados en la ruta y creación del mapa
                encoded_points = paths_data["paths"][0]["points"]
                decoded_points = polyline.decode(encoded_points)

                crear_mapa(orig, dest, decoded_points)

            except KeyError as e:
                 # Manejo de errores al procesar la respuesta JSON de la ruta
                print(f"Error al procesar la respuesta JSON: {e}")
        else:
             # Mensaje de error si no se pudo obtener la ruta correctamente
            print(f"Mensaje de error: {paths_data.get('message', 'No se encontró mensaje de error')}")
            print("*************************************************")

