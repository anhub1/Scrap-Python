from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re
import unicodedata
from utils import extraer_caja_compra, comparar_caja_compra
from utils import extraer_etim, comparar_etim
from utils import extraer_categorias, comparar_categorias
from informe import generar_html
from utils import extraer_menu, comparar_menu
from utils import extraer_busqueda, comparar_busqueda
from utils import imagen, comparar_imagenes



def comparar_webs(url_prod, url_dev, termino_busqueda):
    with sync_playwright() as p:
      
        browser = p.chromium.launch()
        page = browser.new_page()
      

        # --------------------------------------PROD PROCESAR PRODUCCIÓN --------------------------------------------
        
        print(f"Analizando Producción: {url_prod}")
        page.goto(url_prod)
        page.wait_for_timeout(2000)                                    # Esperar un poco a que carguen imágenes
        html_prod = page.content()
        soup_prod = BeautifulSoup(html_prod, 'html.parser')

        # ---------------------------TITLE-------------------------
        titulo_prod = soup_prod.title.string if soup_prod.title else "Sin título"

        # -------------H1 TITULO PRODUCTO----------------------
        h1_tag_prod = soup_prod.find('h1')
        h1_prod = h1_tag_prod.text.strip() if h1_tag_prod else "No encontrado" 
        #print(f"Texto H1 en Prod: {h1_prod}")    

        # --------------------BREADCRUMB--------------------
        breadcrumb_elem_prod = soup_prod.find('div', class_='breadcrumb')
        breadcrumb_prod = breadcrumb_elem_prod.get_text(strip=True) if breadcrumb_elem_prod else "No encontrado"
        #print(f"BREADCRUMB en Prod: {breadcrumb_prod}")

        # -------------------------CATEGORIAS---------------
        cat_prod = extraer_categorias(soup_prod, es_dev=False)


        # --------------------ETIM   TABLA--------------------
        etim_prod = extraer_etim(soup_prod, es_dev=False)


        # --------------------PRECIO INFO PRODUCTO--------------------
        info_prod = extraer_caja_compra(soup_prod, es_dev=False)

        # -------------------------MENÚ-------------------------------
        menu_prod = extraer_menu(soup_prod, es_dev=False)

        # ------------------------ BUSCADOR ------------------------------------------    
        #busqueda_prod = extraer_busqueda(page, "plc", es_dev=False)
        busqueda_prod = extraer_busqueda(page, termino_busqueda, es_dev=False)

        #----------------IMAGEN------------------
        imagen_prod = imagen(soup_prod, es_dev=False)


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------


        # ----------------------------------------DEV PROCESAR DESARROLLO --------------------------------------------
       
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
        
        
        
        
        
        
        # ---------------------------TITLE-------------------------
        titulo_dev = soup_dev.title.string if soup_dev.title else "Sin título"
        
        # -------------H1 TITULO PRODUCTO----------------------
        h1_tag_dev = soup_dev.find('h1')
        h1_dev = h1_tag_dev.text.strip() if h1_tag_dev else "No encontrado"
        #print(f"Texto H1 en DEV: {h1_dev}")
        
        # --------------------BREADCRUMB--------------------
        breadcrumb_elem_dev = soup_dev.find('div', class_='hidden md:flex items-center mb-1')
        if breadcrumb_elem_dev:
            breadcrumb_dev = breadcrumb_elem_dev.get_text(strip=True)
        else:
            breadcrumb_dev = "No encontrado"
        #print(f"BREADCRUMB en Dev: {breadcrumb_dev}")

        # -------------------------CATEGORIAS------------------------ 
        cat_dev = extraer_categorias(soup_dev, es_dev=True)
        
        
        # --------------------ETIM   TABLA---------------------------
        etim_dev = extraer_etim(soup_dev, es_dev=True)
        
        
        # --------------------PRECIO INFO PRODUCTO--------------------
        info_dev = extraer_caja_compra(soup_dev, es_dev=True)
        info_dev["cantidad"] = cantidad_real                                                        # Valor que hemos forzado al inicio
        

        # -------------------------MENÚ-------------------------------
        menu_dev = extraer_menu(soup_dev, es_dev=True)

        # ------------------------ BUSCADOR ------------------------------------------    
        #busqueda_dev = extraer_busqueda(page, "plc", es_dev=True)
        busqueda_dev = extraer_busqueda(page, termino_busqueda, es_dev=True)

        #-----------------IMAGEN-----------------
        imagen_dev = imagen(soup_dev, es_dev=True)


        # Cerrar navegador
        browser.close()

        # -------------------------- RESULTADOS COMPARACIÓN -----------------------------
        print("\n-------- RESULTADOS --------")
        
        print("\n-------- COMPARACIÓN TITLE ---------")
        if titulo_prod == titulo_dev:
            print("✅ Los títulos coinciden.")
        else:
            print(f"❌ Diferencia en títulos:")
            #print(f"   Prod: {titulo_prod}")
            #print(f"   Dev:  {titulo_dev}")

        print("\n-------- COMPARACIÓN DE H1 TITULO ---------")
        if h1_prod == h1_dev:
            print(f"✅ Los H1 coinciden.")
        else:
            print(f"❌ Diferencia en H1:")
            #print(f"   Prod: {h1_prod}")
            #print(f"   Dev:  {h1_dev}")

        print("\n------- COMPARACIÓN DE BREADCRUMB ----------")
        
        bc_prod_clean = breadcrumb_prod.replace(">", "").replace(" ", "").lower()       # Limpiamos símbolos para comparar solo el texto
        bc_dev_clean = breadcrumb_dev.replace(">", "").replace(" ", "").lower()

        if bc_prod_clean == bc_dev_clean:
            print("✅ Los Breadcrumbs coinciden.")
        else:
            print(f"❌ Diferencia en Breadcrumb:")
        """    print(f"   Prod: {breadcrumb_prod}")
            print(f"   Dev:  {breadcrumb_dev}")
            print("-------- Solo texto limpio para comparar: --------")
            print(f"   Prod: {bc_prod_clean}")
            print(f"   Dev:  {bc_dev_clean}")
        """

        # ------------------- COMPARACIÓN DE CATEGORÍAS ----------------------------
        lista_categorias = comparar_categorias(cat_prod, cat_dev)

        # ------------------- COMPARACIÓN ETIM ----------------------------
        lista_etim = comparar_etim(etim_prod, etim_dev)
        
        # ------------------- COMPARACIÓN CAJA DE COMPRA ----------------------------
        lista_compra = comparar_caja_compra(info_prod, info_dev)

        # ---------------------COMPARACIÓN MENÚ-------------------------------
        lista_menu = comparar_menu(menu_prod, menu_dev)

        # ------------------------ BUSCADOR ------------------------------------------ 
        lista_busqueda = comparar_busqueda(busqueda_prod, busqueda_dev)

        #----------------COMPARACIÓN IMAGEN-----------------------
        lista_imagen = comparar_imagenes(imagen_dev, imagen_prod)




        datos_informe = {                       # Crear Diccionario con todos los valores y listas generados
            "url_prod": url_prod,
            "url_dev": url_dev,
            "title": {"prod": titulo_prod, "dev": titulo_dev},
            "h1": {"prod": h1_prod, "dev": h1_dev},
            "breadcrumb": {"prod": breadcrumb_prod, "dev": breadcrumb_dev},
            "categorias": lista_categorias,
            "etim": lista_etim,
            "caja": lista_compra,
            "menu": lista_menu,
            "busqueda": lista_busqueda,
            "imagen": lista_imagen
        }

        generar_html(datos_informe)

        print("\n✅ FIN. Creado el archivo reporte_qa.html")





if __name__ == "__main__":
    URL_PROD = "https://www.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    URL_DEV = "https://fo-dev.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
 
    #comparar_webs(URL_PROD, URL_DEV)
    termino_a_buscar = "pkz"     #input("👉 Introduce el término de búsqueda para comparar: ")
    

    comparar_webs(URL_PROD, URL_DEV, termino_a_buscar)

