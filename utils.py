from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs, unquote

# ------------------------ CATEGORÍAS ------------------------------------------
def extraer_categorias(soup, es_dev=False):
    if not es_dev:
        # ----------------------- PROD -------------------------------------
        datos_cat = []                                                                             # Lista

        menu_prod = soup.find('div', class_='mobile-cat')

        if menu_prod:  
            items = menu_prod.find_all('p')                #todos los párrafos dentro
            for p in items:
                label = p.find('label')
                if label:
                    label.decompose()                                   # eliminamos el <label> si existe (Esto quita la palabra "Categorias:" de la extracción)
                texto = p.get_text(strip=True)                          # Sacamos el texto restante (que será el span o el texto suelto)
                if texto:
                    datos_cat.append(texto)
            
    else:
        # ----------------------- DEV -------------------------------------
        datos_cat = []                                                                              # Lista
       
        menu_dev = soup.find("ul", class_="list-disc")

        if menu_dev:  
            items = menu_dev.find_all("li")
            for li in items:
                texto = li.get_text(strip=True)
                #print(f"Texto DEV: {texto}")
                if texto:
                    datos_cat.append(texto)

    return {
        "cantidad": len(datos_cat),
        "nombres": datos_cat
    }


def comparar_categorias(cat_prod, cat_dev):
    print("\n----------------- COMPARACIÓN DE CATEGORÍAS ------------------")
    resultados_cat = []
    max_cat = max(cat_prod["cantidad"], cat_dev["cantidad"])    # Hay que coger la categoría con más filas 
    
    if cat_prod["cantidad"] == cat_dev["cantidad"]:                           # Número de categorías en este producto
        print(f"✅ Mismo nº categorías ({cat_prod["cantidad"]}).")
    else:
        print(f"❌ Diferente nº categorías: Prod tiene {cat_prod["cantidad"]} y Dev tiene {cat_dev["cantidad"]}.")
    
    cant_p = cat_prod["cantidad"]
    cant_d = cat_dev["cantidad"]
    
    if cant_p == cant_d:
        estado = "✅ OK"
    else:
        estado = "❌ ERROR"
        
    resultados_cat.append({                                 # Guardar en la lista
            "indice": "TOTAL",
            "prod": cant_p,
            "dev": cant_d,
            "estado": estado
        })
    

    print("\n----------------- COMPARACIÓN DETALLADA CATEGORÍAS -----------------")
    
    nombres_p = cat_prod["nombres"]        # Si pongo: [:5] => Máximo 5 para comparar
    nombres_d = cat_dev["nombres"]
    
    for i in range(max_cat):                                    # Recorrer hasta el nº máx de categorías
        if i < cant_p:                                   # Cat dentro de Producción
            info_p = nombres_p[i]
        else:
            info_p = "N/A"
        
        if i < cant_d:                                    # Cat dentro de Desarrollo
            info_d = nombres_d[i]
        else:
            info_d = "N/A"

        if info_p == info_d:
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"
        
        
        resultados_cat.append({                                 # Guardar en la lista
            "indice": i + 1,
            "prod": info_p,
            "dev": info_d,
            "estado": estado
        })
        """
        print(f"{estado} | Nivel {i+1}:")
        print(f"      Prod: {info_p}")
        print(f"      Dev:  {info_d}")
        print("-" * 30)
        """
    return resultados_cat



# -------------------------MENÚ-------------------------------
def extraer_menu(soup, es_dev=False):
    if not es_dev:
        # ----------------------- PROD -------------------------------------
        datos_menu = []                                                                             # Lista

        menu_prod = soup.find('div', class_='jetmenu-wrapper')

        if menu_prod:  
            items = menu_prod.find_all('li')                #todos los li
            for li in items:
                enlace = li.find('a')
                if enlace:
                    texto = enlace.get_text(strip=True)
                    enlace_url = enlace.get('href', '')     # Si no hay enlace mete vacío: ' '
                    #print(f"Texto PROD: {texto}")
                    #print(f"Enlace PROD: {enlace_url}")
                    if texto:
                        datos_menu.append({
                            "texto": texto, 
                            "url": enlace_url
                        })
            
    else:
        # ----------------------- DEV -------------------------------------
        datos_menu = []                                                                             # Lista

        menu_dev = soup.find(attrs={'data-testid':'background'})

        if menu_dev:  
            items = menu_dev.find_all('a')                  #todos los a
            for a in items:
                texto = a.get_text(strip=True)
                enlace_url = a.get('href', '')                  # Si no hay enlace mete vacío
                #print(f"Texto DEV: {texto}")
                #print(f"Enlace DEV: {enlace_url}")
                if texto:
                    datos_menu.append({
                        "texto": texto, 
                        "url": enlace_url
                    })

    return {
        "cantidad": len(datos_menu),
        "nombres": datos_menu
    }

def comparar_menu(menu_prod, menu_dev):
    print("\n----------------- COMPARACIÓN DE MENÚ ------------------------")
    resultados_menu = []
    max_cat = max(menu_prod["cantidad"], menu_dev["cantidad"])    # Hay que coger la categoría con más filas 
    
    
    if menu_prod["cantidad"] == menu_dev["cantidad"]:
        print(f"✅ Mismo Nº de elementos ({menu_prod["cantidad"]}).")
    else:
        print(f"❌ Diferencia: Prod tiene {menu_prod["cantidad"]} y Dev tiene {menu_dev["cantidad"]}.")
        
    cant_p = menu_prod["cantidad"]
    cant_d = menu_dev["cantidad"]
    
    if cant_p == cant_d:
        estado = "✅ OK"
    else:
        estado = "❌ ERROR"
        
    resultados_menu.append({                        # Guardar en la lista para el HTML
            "indice": "TOTAL",
            "texto_p": cant_p,
            "url_p": "--",
            "texto_d": cant_d,
            "url_d": "--",
            "estado": estado
        })    
    #-----------------------------------------------------------------------
    
    nombres_p = menu_prod["nombres"]        # Si pongo: [:5] => Máximo 5 para comparar
    nombres_d = menu_dev["nombres"]
    
    for i in range(max_cat):                      # Usamos el largo de PROD para iterar (fila a fila)
        if i < len(nombres_p):
            info_p = nombres_p[i]
            texto_p = str(info_p.get("texto", "N/A")).strip()
            url_p = str(info_p.get('url', 'N/A')).strip()
        else:
            texto_p = "N/A"
            url_p = "N/A"
            
        if i < len(nombres_d):
            info_d = nombres_d[i]
            texto_d = str(info_d.get("texto", "N/A")).strip()
            url_d = str(info_d.get('url', 'N/A')).strip()
        else:
            texto_d = "N/A"
            url_d = "N/A"    
        
        if texto_p == texto_d and url_p == url_d:       # Si coinciden texto y URL
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"
            
        
        resultados_menu.append({                        # Guardar en la lista para el HTML
            "indice": i+1,
            "texto_p": texto_p,
            "url_p": url_p,
            "texto_d": texto_d,
            "url_d": url_d,
            "estado": estado
        })
        """
        # Print por consola
        print(f"{estado} | Fila {i+1}:")
        print(f"      PROD: {texto_p} -> {url_p}")
        print(f"      DEV:  {texto_d} -> {url_d}")
        print("-" * 30)
        """
    return resultados_menu







# ------------------------ ETIM   TABLA ------------------------------------------
def extraer_etim(soup, es_dev=False):

    if not es_dev:
        # ----------------------- PROD -------------------------------------
        datos_etim = []                                                                             # Lista

        encabezado_etim = soup.find(['h2', 'h3'], string=re.compile("ETIM", re.IGNORECASE))         # Buscar h2 o h3 que contenga "ETIM" (ignorando mayúsculas/minúsculas)

        if encabezado_etim:
            tabla_etim = encabezado_etim.find_next('table')            
            if tabla_etim:
                filas = tabla_etim.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all('td')
                    
                    if len(celdas) >= 2:                                                            # Solo procesamos si hay al menos 2 celdas (Nombre y Valor)
                        caracteristica = celdas[0].get_text(strip=True)                             # Columna CARACTERÍSTICA
                        valor = celdas[1].get_text(strip=True)                                      # Columna VALOR
                        unidad = celdas[2].get_text(strip=True) if len(celdas) > 2 else ""          # Columna UNIDAD=> si existe la tercera celda
                        
                        datos_etim.append ({                                              # Guardar en Lista
                            'nombre': caracteristica,
                            'valor': valor,
                            'unidad': unidad
                        })
            
    else:
        # ----------------------- DEV -------------------------------------
        datos_etim = []                                                                              # Lista
       
        div_etim_dev = soup.find('div', id='productETIM')

        if div_etim_dev:
            tabla_etim_dev = div_etim_dev.find('table')
            if tabla_etim_dev:
                filas = tabla_etim_dev.find_all('tr')
                
                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        caracteristica = celdas[0].get_text(strip=True)                             # Columna CARACTERÍSTICA
                        valor = celdas[1].get_text(strip=True)                                      # Columna VALOR
                        unidad = celdas[2].get_text(strip=True) if len(celdas) > 2 else ""          # Columna UNIDAD=> si existe la tercera celda
                        
                        datos_etim.append ({
                            'nombre': caracteristica,
                            'valor': valor,
                            'unidad': unidad
                        })

    return datos_etim

def comparar_etim(etim_prod, etim_dev):
    print("\n----------------- COMPARACIÓN DE ETIM ------------------------")
        
    if len(etim_prod) == len(etim_dev):
        print(f"✅ Ambas tienen la misma cantidad de características ({len(etim_prod)}).")
    else:
        print(f"❌ Diferencia en cantidad: Prod tiene {len(etim_prod)} y Dev tiene {len(etim_dev)}.")
        
    print("\n----------------- COMPARACIÓN DETALLADA ETIM -----------------")
    resultados_etim = []
    
    cant_p = len(etim_prod)
    cant_d = len(etim_dev)

    max_etim = max(cant_p, cant_d)
    
    if cant_p == cant_d:
        estado = "✅ OK"
    else:
        estado = "❌ ERROR"

    resultados_etim.append({                                                                # Guardar en la lista
            "indice": "TOTAL",
            "nombre_p": cant_p,
            "valor_p": "--",
            "unidad_p": "--",
            "nombre_d": cant_d,
            "valor_d": "--",
            "unidad_d": "--",
            "estado": estado
    })
    
    for i in range(max_etim):                                                             # Comparar fila a fila
                                                                           
        if i < len(etim_prod):                                                                 # Coger la fila de PROD
            info_p = etim_prod[i]
        else:
            info_p = {"nombre": "N/A", "valor": "N/A", "unidad": ""}
        
        if i < len(etim_dev):                                                                   # La tabla de PROD tiene más filas de DEV
            info_d = etim_dev[i]
        else:
            info_d = {"nombre": "N/A", "valor": "N/A", "unidad": ""}                            # Si ya no hay filas en DEV poner NA
        
        nombre_p = str(info_p.get("nombre", "N/A")).strip()
        valor_p = str(info_p.get('valor', 'N/A')).strip()          
        unidad_p = str(info_p.get('unidad', '')).strip()
        
        nombre_d = str(info_d.get("nombre", "N/A")).strip()
        valor_d = str(info_d.get('valor', 'N/A')).strip()
        unidad_d = str(info_d.get('unidad', '')).strip()

            
        if nombre_p == nombre_d and valor_p == valor_d and unidad_p == unidad_d:
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"
            
            
        resultados_etim.append({                                                                # Guardar en la lista
            "indice": i+1,
            "nombre_p": nombre_p,
            "valor_p": valor_p,
            "unidad_p": unidad_p,
            "nombre_d": nombre_d,
            "valor_d": valor_d,
            "unidad_d": unidad_d,
            "estado": estado
        })
        """
        print(f"{estado} | Comparando campos:")
        print(f"      Nombre PROD: {nombre_p}")
        print(f"      Nombre DEV:  {nombre_d}")
        print(f"      -> Val PROD: {valor_p}{unidad_p}")
        print(f"      -> Val DEV:  {valor_d}{unidad_d}")
        print("-" * 30)
        """
    return resultados_etim    
    



# ------------------------ CAJA DE COMPRA Y PRECIOS ------------------------------------------
def extraer_caja_compra(soup, es_dev=False):
    datos = {
        "precio_unitario": "0",
        "precio_total": "0",
        "cantidad": "0",
        "texto_descuentos": "N/A",  
        "texto_actualizar": "N/A"
    }
    
    if not es_dev:
        # ----------------------- PROD -------------------------------------
        contenedor_prod = soup.find("div", class_="content_prices")                                                 # Buscar solo en el contenedor de precios
        
        if contenedor_prod:
            precio_uni = contenedor_prod.find("span", id="our_price_display")
            precio_tot = contenedor_prod.find("span", id="our_price_display_total")
            precio_info = contenedor_prod.find("span", class_="price-info")                                             # Info del precio de unidad
            link_registro = contenedor_prod.find("a", id="shaker")                                                  # Link del registro
            cantidad = soup.find("input", id="quantity_wanted")
            
            datos["precio_unitario"] = precio_uni.get_text(strip=True) if precio_uni else "N/A"
            datos["precio_total"] = precio_tot.get_text(strip=True) if precio_tot else "N/A"
            datos["texto_descuentos"] = precio_info.get_text(strip=True) if precio_info else "N/A"
            #print(f"✅ Texto Descuentos guardado: {datos['texto_descuentos']}")
            datos["texto_actualizar"] = link_registro.get_text(strip=True) if link_registro else "N/A"
            datos["cantidad"] = cantidad.get("value") if cantidad else "1"
        
        else:                                                                                                       # Buscar en HTML si no encuentra
            precio_uni = soup.find("span", id="our_price_display")
            precio_tot = soup.find("span", id="our_price_display_total")
            cantidad = soup.find("input", id="quantity_wanted")
            precio_info = soup.find("span", class_="price-info")                                             # Info del precio de unidad
            link_registro = soup.find("a", id="shaker")
            
            datos["precio_unitario"] = precio_uni.get_text(strip=True) if precio_uni else "N/A"
            datos["precio_total"] = precio_tot.get_text(strip=True) if precio_tot else "N/A"
            datos["cantidad"] = cantidad.get("value") if cantidad else "1"     
        
    else:
        # ----------------------- DEV -------------------------------------                                                                                               # Precio unitario siempre existe.
        nodo_p = soup.find("p", string=re.compile("Precio Unitario", re.IGNORECASE))                                # Coger el p que contiene Precio Unitario
        contenedor_precios = nodo_p.find_parent("div") if nodo_p else None                                          # Coger el div que contiene Precio Unitario
        
        if contenedor_precios:
            todos_los_p = contenedor_precios.find_all("p")                                                          # Solo los <p> dentro del contenedor de precios
            for p in todos_los_p:
                texto = p.get_text(strip=True).upper()                                                              # Resultado= PRECIO TOTAL: 510,75 €
                #print(f"Texto en <p> dentro del contenedor de precios: {texto}")
                if "PRECIO UNITARIO" in texto:
                    datos["precio_unitario"] = texto.split(":")[-1].strip()                                         # Resultado= 510,75 €
                    #print(f"Precio Unitario encontrado en DEV: {datos['precio_unitario']}")
                if "PRECIO TOTAL" in texto:
                    datos["precio_total"] = texto.split(":")[-1].strip()                                            # Resultado= 170,25 €
                    #print(f"Precio Total encontrado en DEV: {datos['precio_total']}")
                    
            for elemento in contenedor_precios.find_all(string=True):
                texto_limpio = elemento.strip()
                texto_mayus = texto_limpio.upper()
                
                if "DESCUENTOS" in texto_mayus:
                    datos["texto_descuentos"] = texto_limpio
                    #print(f"✅ Texto Descuentos guardado: {texto_limpio}")
                
                if "ACTUALIZAR" in texto_mayus:
                    datos["texto_actualizar"] = texto_limpio
                    #print(f"✅ Texto Actualizar guardado: {texto_limpio}")
    return datos


def comparar_caja_compra(info_prod, info_dev):
        print("\n----------------- COMPARACION CAJA DE COMPRA -------------")
        
        resultados_caja = []
        campos_a_comparar = [
            "precio_unitario", 
            "precio_total", 
            "cantidad", 
            "texto_descuentos", 
            "texto_actualizar"
        ]

        for clave in campos_a_comparar:
            valor_p = str(info_prod.get(clave, "N/A")).strip()                                        # str => transforma a texto para evitar problemas al comparar
            valor_d = str(info_dev.get(clave, "N/A")).strip()
            
            # Lógica de comparación
            if clave.startswith("texto"):
                compara = valor_p.upper().replace(".", "") == valor_d.upper().replace(".", "")        # Para textos comparar en mayus y quitando espacios mejor
            else:
                compara = valor_p == valor_d                                                          # Para numeros se compara tal cual el valor
            
            if compara:
                estado = "✅ OK"
            else:
                estado = "❌ ERROR"
            
            # Guardar en la lista para el informe
            resultados_caja.append({
                "campo": clave.replace("_", " ").title(),
                "prod": valor_p,
                "dev": valor_d,
                "estado": estado
            })
            """
            print(f"{estado} | {clave.replace('_', ' ').title()}:")
            print(f"      Prod: {valor_p}")
            print(f"      Dev:  {valor_d}")
            """
        return resultados_caja
    
    
# ------------------------ BUSCADOR ------------------------------------------    
    
def extraer_busqueda(page, termino, es_dev=False):
    if not es_dev:
        # ----------------------- PROD -------------------------------------
        selector_input = "#search_query_top"
        clase_productos = "#resultados_busqueda tbody tr"       # Seleccionamos las filas de la tabla de resultados de PROD
        selector_codfabricante = ".cod_fabricante"              # Selector codigo fabricante en PROD
        selector_nombre = ".product-descor"                     # Selector descripcion o titulo en PROD
        selector_contenedor_resultados = "#resultados_busqueda"
    else:
        # --- CONFIG DEV ---
        selector_input = "#txtProduct2FindMobile"
        clase_productos = "div[data-testid='products-view'] #horizontal-card" # Clase que usa el diseño en DEV
        selector_referencia_dev = ".cp p:last-child span"                   # Selector codigo fabricante en DEV
        selector_nombre = ".title p"                                        # Nombre dentro de cada fila de resultados.
        selector_contenedor_resultados = "div[data-testid='products-view']"
        
    print(f"Buscando '{termino}' en {'DEV' if es_dev else 'PROD'}...")

    
    page.fill(selector_input, termino)
    page.press(selector_input, "Enter")
    
    
    page.wait_for_load_state("networkidle")                         # Esperar a que la nueva página (resultados) cargue
    
    if not es_dev:                                                  # Retardo para mostrar resultados
        page.wait_for_selector("#resultados_busqueda", timeout=5000)
    else:
        page.wait_for_selector("div[data-testid='products-view']", timeout=5000)    
    
    
    # CREAR EL NUEVO SOUP: es un html nuevo de la página nueva
    nuevo_html = page.content()
    nuevo_soup = BeautifulSoup(nuevo_html, 'html.parser')
    
    items = nuevo_soup.select(clase_productos)              # Extraer los datos de la lista de productos
    lista_nombres = []
    for it in items:
        elemento_nombre = it.select_one(selector_nombre)    # Busca nombre en cada fila de toda la tabla
        nombre = elemento_nombre.get_text(strip=True) if elemento_nombre else "Sin nombre"
        
        if not es_dev:
            elemento_ref = it.select_one(selector_codfabricante)    # Extraer Referencia en PROD
            referencia = elemento_ref.get_text(strip=True) if elemento_ref else "N/A" 
        else:
            elemento_ref = it.select_one(selector_referencia_dev)   # Extraer Referencia en DEV
            referencia = elemento_ref.get_text(strip=True) if elemento_ref else "N/A"
            
        #lista_nombres.append(f"{referencia} - {nombre}")   
        lista_nombres.append({
            "referencia": referencia,
            "nombre": nombre
            })
        
    #print(f"✅ Encontrados {len(items)} productos en {'DEV' if es_dev else 'PROD'}.")
    return {
        "cantidad": len(items),
        "nombres": lista_nombres,
        "termino": termino
    }

def comparar_busqueda(busqueda_prod, busqueda_dev):
    print("\n----------------- COMPARACIÓN DE BÚSQUEDA ------------------------")
    resultados_busqueda = []
    # Comprobamos la cantidad total primero
    if busqueda_prod["cantidad"] == busqueda_dev["cantidad"]:
        print(f"✅ Mismo nº de resultados ({busqueda_prod['cantidad']}).")
    else:
        print(f"❌ Diferencia en cantidad: Prod tiene {busqueda_prod['cantidad']} y Dev tiene {busqueda_dev['cantidad']}.")
          
    cant_p = busqueda_prod["cantidad"]
    cant_d = busqueda_dev["cantidad"]
    
    if cant_p == cant_d:
        estado = "✅ OK"
    else:
        estado = "❌ ERROR"
    
    
    resultados_busqueda.append({                    # La añadimos como primera posición en la lista
        "posicion": "TOTAL",
        "prod_ref": cant_p,
        "prod_titulo": "--",
        "dev_ref": cant_d,
        "dev_titulo": "--",
        "estado": estado
    })
        
               
    print("\n----------------- COMPARACIÓN DETALLADA RESULTADOS -----------------")
    
    
   
    nombres_p = busqueda_prod["nombres"]        # Si pongo: [:5] => Máximo 5 para comparar
    nombres_d = busqueda_dev["nombres"]
    max_filas = max(len(nombres_p), len(nombres_d))
    
    for i in range(max_filas):
        if i < len(nombres_p):
            info_p = nombres_p[i]
            referencia_p = info_p.get("referencia", "N/A").strip()
            nombre_p = info_p.get("nombre", "N/A").strip()
        else:
            referencia_p = "N/A"
            nombre_p = "N/A"
            
        if i < len(nombres_d):
            info_d = nombres_d[i]
            referencia_d = info_d.get("referencia", "N/A").strip()
            nombre_d = info_d.get("nombre", "N/A").strip()
        else:                                   # Si en DEV hay menos resultados que en PROD
            referencia_d = "N/A"
            nombre_d = "N/A"                         
            
        if referencia_p == referencia_d:        #Comparar por la referencia solamente
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"
            
        resultados_busqueda.append({                # Guardar en la lista para HTML
            "posicion": i + 1,
            "prod_ref": referencia_p,
            "prod_titulo": nombre_p,
            "dev_ref": referencia_d,
            "dev_titulo": nombre_d,
            "estado": estado
        })
        """X
        # Print por consola
        print(f"{estado} | Posición {i+1}:")
        print(f"      PROD: {info_p}")
        print(f"      DEV:  {info_d}")
        print("-" * 30)
        """
    return resultados_busqueda
    
    
# ------------------------ IMAGENES ------------------------------------------  

def imagen(soup, es_dev=False):
    imagenes = []
    
    if not es_dev:
        #------PROD-----

        img_tag_prod = soup.find("div", id="image-block")

        if img_tag_prod:
            for img in img_tag_prod.find_all("img"):
                img_src = img.get("src")
                if img_src:
                    imagenes.append(img_src)
                    
    
    else:
        #----------DESARROLLO------------
        def extraer_imagen(src): #obtener url limpia como se muestra en producción
            if not src:
                return None
                
            if "/_next/image" in src:
                parse = urlparse(src)
                params_img = parse_qs(parse.query)
                if "url" in params_img:
                    return unquote(params_img["url"][0])
                
            return src
            
        img_tag_dev = soup.find("div", class_="swiper-wrapper")

        if img_tag_dev:
            for img in img_tag_dev.find_all("img"):
                src = img.get("src")
                imagen = extraer_imagen(src)
                if imagen:
                    imagenes.append(imagen)
                    
    return imagenes

def comparar_imagenes(img_dev, img_prod):

    resultados = []

    cant_p = len(img_prod)
    cant_d = len(img_dev)

    max_img = max(cant_p, cant_d)

    if cant_p == cant_d:
        estado = "✅ OK"
    else:
        estado = "❌ ERROR"

    resultados.append({
            "indice": "TOTAL",
            "imagen_p": cant_p,
            "imagen_d": cant_d,
            "estado": estado
        })

    for i in range(max_img):

        info_p = img_prod[i] if i < cant_p else "N/A"
        info_d = img_dev[i] if i < cant_d else "N/A"

        if info_p == info_d:
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"

        resultados.append({
            "indice": i+1,
            "imagen_p": info_p,
            "imagen_d": info_d,
            "estado": estado
        })

    return resultados  