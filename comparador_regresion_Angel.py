from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re
import unicodedata

def comparar_webs(url_prod, url_dev):
    with sync_playwright() as p:
      
        browser = p.chromium.launch()
        page = browser.new_page()
      

        # --- PROCESAR PRODUCCIÓN ---
        print(f"Analizando Producción: {url_prod}")
        page.goto(url_prod)
        page.wait_for_timeout(2000)                                    # Esperar un poco a que carguen imágenes
        html_prod = page.content()
        soup_prod = BeautifulSoup(html_prod, 'html.parser')

        # ---------------TITLE---------------
        titulo_prod = soup_prod.title.string if soup_prod.title else "Sin título"

        # -------------H1 TITULO PRODUCTO----------------------
        h1_tag_prod = soup_prod.find('h1')
        h1_prod = h1_tag_prod.text.strip() if h1_tag_prod else "No encontrado" 
        print(f"Texto H1 en Prod: {h1_prod}")    

        # --------------------BREADCRUMB--------------------
        breadcrumb_elem_prod = soup_prod.find('div', class_='breadcrumb')
        breadcrumb_prod = breadcrumb_elem_prod.get_text(strip=True) if breadcrumb_elem_prod else "No encontrado"
        #print(f"BREADCRUMB en Prod: {breadcrumb_prod}")

        # -------------------------CATEGORIAS-------------Buscamos el div con clase 'mobile-cat'
        div_categorias_prod = soup_prod.find('div', class_='mobile-cat')
        categorias_prod = []

        if div_categorias_prod:  
            parrafos = div_categorias_prod.find_all('p')                #todos los párrafos dentro
            for p in parrafos:
                label = p.find('label')
                if label:
                    label.decompose()                                   # eliminamos el <label> si existe (Esto quita la palabra "Categorias:" de la extracción)
                texto = p.get_text(strip=True)                          # Sacamos el texto restante (que será el span o el texto suelto)
                if texto:
                    categorias_prod.append(texto)

        #print(f"Categorías PROD extraídas: {categorias_prod}")


        # --------------------ETIM   TABLA--------------------
        etim_prod = {}                                                                              # Diccionario

        encabezado_etim = soup_prod.find(['h2', 'h3'], string=re.compile("ETIM", re.IGNORECASE))    # Buscar h2 o h3 que contenga "ETIM" (ignorando mayúsculas/minúsculas)

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
                        
                        etim_prod[caracteristica] = {                                               # Guardar en Diccionario
                            'valor': valor,
                            'unidad': unidad
                        }

        print(f"ETIM Prod extraído: {len(etim_prod)} características encontradas.")
        for caracteristica, datos in etim_prod.items():
            v = datos['valor']
            u = datos['unidad']
            print(f"🔹 {caracteristica}: {v} (Unidad: {u})")



        # --------------------PRECIO INFO PRODUCTO--------------------
        info_prod = extraer_caja_compra(soup_prod, es_dev=False)






#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------


        # --- PROCESAR DESARROLLO ---
        print(f"Analizando Desarrollo: {url_dev}")
        page.goto(url_dev)
        
        # ---------------- FORZAR CANTIDAD DE PRODUCTOS = 3 EN DEV ----------------
        input_selector = "input[type='number']"
        page.wait_for_selector(input_selector)
        page.click(input_selector)                                      # Simula hacer click en input
        page.fill(input_selector, "3")                                  # Meter un 3 en el input
        page.press(input_selector, "Enter")                             # Presionar Enter
        cantidad_real = page.input_value("input[type='number']")        # Cojo el valor que hemos forzado en page.fill
        page.wait_for_timeout(2000)
        html_dev = page.content()
        soup_dev = BeautifulSoup(html_dev, 'html.parser')
        
        
        
        
        
        
        
        titulo_dev = soup_dev.title.string if soup_dev.title else "Sin título"
        
        # -------------H1 TITULO PRODUCTO----------------------
        h1_tag_dev = soup_dev.find('h1')
        h1_dev = h1_tag_dev.text.strip() if h1_tag_dev else "No encontrado"
        print(f"Texto H1 en DEV: {h1_dev}")
        
        # --------------------BREADCRUMB--------------------
        breadcrumb_elem_dev = soup_dev.find('div', class_='hidden md:flex items-center mb-1')
        if breadcrumb_elem_dev:
            breadcrumb_dev = breadcrumb_elem_dev.get_text(strip=True)
        else:
            breadcrumb_dev = "No encontrado"
        #print(f"BREADCRUMB en Dev: {breadcrumb_dev}")

        # -------------------------CATEGORIAS------------- <ul> que tiene las clases de Tailwind de la lista de categorías
        div_categorias_dev = soup_dev.find("ul", class_="list-disc list-inside mb-1")        
        categorias_dev = div_categorias_dev.get_text(strip=True) if div_categorias_dev else "No encontrado"
        #print(f"Texto div Categorias DEV: {categorias_dev}")
        
        
        # --------------------ETIM   TABLA--------------------
        etim_dev = {}                                                                                           # Diccionario
       
        div_etim_dev = soup_dev.find('div', id='productETIM')

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
                        
                        etim_dev[caracteristica] = {
                            'valor': valor,
                            'unidad': unidad
                        }

        print(f"ETIM Dev extraído: {len(etim_dev)} características encontradas.")
        for caracteristica, datos in etim_dev.items():
            v = datos['valor']
            u = datos['unidad']
            print(f"🔹 {caracteristica}: {v} (Unidad: {u})")
        
        # --------------------PRECIO INFO PRODUCTO--------------------
        info_dev = extraer_caja_compra(soup_dev, es_dev=True)
        info_dev["cantidad"] = cantidad_real                                                        # Valor que hemos forzado al inicio
        

        # Cerrar navegador
        browser.close()

        
        print("\n-------- RESULTADOS --------")
        print("\n-------- COMPARACIÓN TITLE ---------")
        if titulo_prod == titulo_dev:
            print("✅ Los títulos coinciden.")
        else:
            print(f"❌ Discrepancia en títulos:")
            print(f"   Prod: {titulo_prod}")
            print(f"   Dev:  {titulo_dev}")

        print("\n-------- COMPARACIÓN DE H1 TITULO ---------")
        if h1_prod == h1_dev:
            print(f"✅ Los H1 coinciden.")
        else:
            print(f"❌ Discrepancia en H1:")
            print(f"   Prod: {h1_prod}")
            print(f"   Dev:  {h1_dev}")

        print("\n------- COMPARACIÓN DE BREADCRUMB ----------")
        
        bc_prod_clean = breadcrumb_prod.replace(">", "").replace(" ", "").lower()       # Limpiamos símbolos para comparar solo el texto
        bc_dev_clean = breadcrumb_dev.replace(">", "").replace(" ", "").lower()

        if bc_prod_clean == bc_dev_clean:
            print("✅ Los Breadcrumbs coinciden.")
        else:
            print(f"❌ Discrepancia en Breadcrumb:")
            print(f"   Prod: {breadcrumb_prod}")
            print(f"   Dev:  {breadcrumb_dev}")
            print("-------- Solo texto limpio para comparar: --------")
            print(f"   Prod: {bc_prod_clean}")
            print(f"   Dev:  {bc_dev_clean}")

        # --- COMPARACIÓN DE CATEGORÍAS ---
        print("\n------ COMPARACIÓN DE CATEGORÍAS -----------")
        if categorias_dev == categorias_prod:
            print("✅ Los div de categoria coinciden.")
        else:
            print(f"❌ Discrepancia en div categoria:")
            print(f"   Prod: {categorias_prod}")
            print(f"   Dev:  {categorias_dev}")

        
        print("\n------ COMPARACIÓN DE ETIM -----------")
        
        if len(etim_prod) == len(etim_dev):
            print(f"✅ Ambas tienen la misma cantidad de características ({len(etim_prod)}).")
        else:
            print(f"❌ Diferencia en cantidad: Prod tiene {len(etim_prod)} y Dev tiene {len(etim_dev)}.")
        
        print("\n------- COMPARACIÓN DETALLADA ETIM -------")
        errores_encontrados = 0

        for caracteristica, datos_prod in etim_prod.items():                                                # Cogemos cada característica de Producción y sus datos (valor y unidad)
            
            datos_dev = etim_dev.get(caracteristica)                                                        # Buscar la misma característica en DEV

            if datos_dev is None:                                                                           # Si no existe esa característica en DEV, es un error
                print(f"❌ {caracteristica}: No existe en la web de Desarrollo.")
                errores_encontrados += 1
                continue
         
            v_prod, u_prod = datos_prod['valor'], datos_prod['unidad']                                      # Extraer VALOR y UNIDAD de Producción
            v_dev, u_dev = datos_dev['valor'], datos_dev['unidad']                                          # Extraer VALOR y UNIDAD de Desarrollo

            if v_prod == v_dev and u_prod == u_dev:
                print(f"✅ {caracteristica}: Coincide ({v_prod} {u_prod})")
            else:
                print(f"❌ {caracteristica}: DISCREPANCIA")
                print(f"   -> Prod: {v_prod} {u_prod}")
                print(f"   -> Dev:  {v_dev} {u_dev}")
                errores_encontrados += 1

        if errores_encontrados == 0:
            print("\n✅ Todos los datos son idénticos.")
        

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
            print(f"{estado} | {clave.replace('_', ' ').title()}:")
            print(f"      Prod: {valor_p}")
            print(f"      Dev:  {valor_d}")


# ------------------ FUNCION EXTRAER CAJA COMPRA (PRECIO, STOCK, CANTIDAD) ------------------
def extraer_caja_compra(soup, es_dev=False):
    datos = {
        "precio_unitario": "0",
        "precio_total": "0",
        "cantidad": "0",
        "texto_descuentos": "N/A",  
        "texto_actualizar": "N/A"
    }
    
    if not es_dev:
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
            print(f"✅ Texto Descuentos guardado: {datos['texto_descuentos']}")
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
        # --- DEV ---                                                                                               # Precio unitario siempre existe.
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
                    print(f"✅ Texto Descuentos guardado: {texto_limpio}")
                
                if "ACTUALIZAR" in texto_mayus:
                    datos["texto_actualizar"] = texto_limpio
                    print(f"✅ Texto Actualizar guardado: {texto_limpio}")
    return datos









if __name__ == "__main__":
    URL_PROD = "https://www.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    #URL_PROD = "https://www.electricautomationnetwork.com/pt/siemens/3na3124-6-3na31246-siemens-lv-hrc-fuse-link-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-front-indicator-n"
    #URL_DEV = "https://fo-dev.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    URL_DEV = "https://fo-dev.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    
    comparar_webs(URL_PROD, URL_DEV)
