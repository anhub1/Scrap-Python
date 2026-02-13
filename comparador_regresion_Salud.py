from urllib.parse import urlparse, parse_qs, unquote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

def comparar_webs(url_prod, url_dev):
    with sync_playwright() as p:
      
        browser = p.chromium.launch()
        page = browser.new_page()
      

        # --- PROCESAR PRODUCCIÓN ---
        print(f"Analizando Producción: {url_prod}")
        page.goto(url_prod)
        page.wait_for_timeout(1000)                                   
        html_prod = page.content()
        soup_prod = BeautifulSoup(html_prod, 'html.parser')

        # ---TITLE---
        titulo_prod = soup_prod.title.string if soup_prod.title else "Sin título"

        # ---H1 TITULO PRODUCTO---
        h1_tag_prod = soup_prod.find('h1')
        h1_prod = h1_tag_prod.text.strip() if h1_tag_prod else "No encontrado"     

        # ---BREADCRUMB---
        breadcrumb_elem_prod = soup_prod.find('div', class_='breadcrumb')
        breadcrumb_prod = breadcrumb_elem_prod.get_text(strip=True) if breadcrumb_elem_prod else "No encontrado"
        
        # ---CATEGORIAS---
        div_categorias_prod = soup_prod.find('div', class_='mobile-cat')
        categorias_prod = []

        if div_categorias_prod:  
            parrafos = div_categorias_prod.find_all('p')                
            for p in parrafos:
                label = p.find('label')
                if label:
                    label.decompose()                                   
                texto = p.get_text(strip=True)                          
                if texto:
                    categorias_prod.append(texto)
        else: 
            print("No encontrado")

        #---DIV MENÚ---
        div_menu_prod = soup_prod.find('div', class_='jetmenu-wrapper')
        menu_prod = div_menu_prod.get_text(strip=True) if div_menu_prod else "No encontrado"

        #---Referencia, Fabricante, Descripción, uds/embalaje

        ref_tag_prod = soup_prod.find("p", id ="product_reference")
        ref_prod = ref_tag_prod.get_text(strip=True) if ref_tag_prod else "No encontrado"


        fabricante_tag_prod = soup_prod.find("p", id="product_manufacturer")
        fabricante_prod = []

        if fabricante_tag_prod:
            for label in fabricante_tag_prod.find_all("label"):
                if "Fabricante" in label.text:
                    span = label.find_next_sibling("span")
                    if span:
                        texto_limpio = f"{label.text} {span.text}"
                        fabricante_prod.append(texto_limpio)
        else: 
            print("No encontrado")


        description_tag_prod = soup_prod.find("div", id ="short_description_block")
        descripcion_prod = []

        #label = description_tag_prod.find("label").get_text(strip=True)
        if description_tag_prod:
            for p in description_tag_prod.find_all("p", class_="buttons_bottom_block"):
                p.decompose()
                for p in description_tag_prod.find_all("p"):
                    texto = p.get_text(strip=True)
                    if texto:
                        descripcion_prod.append(texto) 
        else: 
            print("No encontrado")
        
        uds_tag_prod = soup_prod.find("p", id="product_codigo")
        uds_prod  = []

        if uds_tag_prod:
            for label in uds_tag_prod.find_all("label"):
                if "Unidades por embalaje" in label.text:
                    span = label.find_next_sibling("span")
                    if span:
                        texto_limpio = f"{label.text} {span.text}"
                        uds_prod.append(texto_limpio)
        else: 
            uds_prod = "No encontrado"                  
                

        #---------------------------------
        # --- PROCESAR DESARROLLO ---
        print(f"Analizando Desarrollo: {url_dev}")
        page.goto(url_dev)
        page.wait_for_timeout(1000)
        page.screenshot(path="screenshots/dev.png")
        html_dev = page.content()
        soup_dev = BeautifulSoup(html_dev, 'html.parser')

        #---TITLE HEAD---
        titulo_dev = soup_dev.title.string if soup_dev.title else "Sin título"
        
        # ---H1 TITULO PRODUCTO---
        h1_tag_dev = soup_dev.find('h1')
        h1_dev = h1_tag_dev.text.strip() if h1_tag_dev else "No encontrado"
                
        # ---BREADCRUMB---
        breadcrumb_elem_dev = soup_dev.find('div', class_='hidden md:flex items-center mb-1')
        if breadcrumb_elem_dev:
            breadcrumb_dev = breadcrumb_elem_dev.get_text(strip=True)
        else:
            breadcrumb_dev = "No encontrado"
        
        # ---CATEGORIAS---
        div_categorias_dev = soup_dev.find("ul", class_="list-disc list-inside mb-1")        
        categorias_dev = div_categorias_dev.get_text(strip=True) if div_categorias_dev else "No encontrado"
        
        #---MENÚ---
        div_menu_dev = soup_dev.find("div", class_="px-5 bg-white hidden lg:block")
        menu_dev = div_menu_dev.get_text(strip=True) if div_menu_dev else "No encontrado"

        #---Referencia, fabricante, descripción, uds/embalaje---

        div_rfd = soup_dev.find("div", class_="col-span-12 lg:col-span-6 text-base")
        p_tag = []

        if div_rfd:
            parrafos = div_rfd.find_all("p")
            for p in parrafos:
                texto = p.get_text(strip=True)
                if texto:
                    p_tag.append(texto)
        else:
            print("No se encontró")

        ref_dev = p_tag[0]
        fabricante_dev = p_tag[1]
        descripcion_dev = p_tag[2]

        uds_tag_dev = soup_dev.find("p", id="product_codigo")
        uds_dev  = []

        if uds_tag_dev:
            for label in uds_tag_dev.find_all("label"):
                if "Referencia" in label.text:
                    span = label.find_next_sibling("span")
                    if span:
                        texto_limpio = f"{label.text} {span.text}"
                        uds_dev.append(texto_limpio)
        else: 
            uds_dev = "No encontrado"   
        
        #---IMAGENES DEV---

        def extraer_imagen(src): #obtener url limpia como se muestra en producción
            if not src:
                return None
            
            if "/_next/image" in src:
                parse = urlparse(src)
                params_img = parse_qs(parse.query)
                if "url" in params_img:
                    return unquote(params_img["url"][0])
            
            return src
        
        img_tag_dev = soup_dev.find("div", class_="swiper-wrapper")
        img_dev = []

        if img_tag_dev:
            for img in img_tag_dev.find_all("img"):
                src = img.get("src")
                imagen = extraer_imagen(src)
                if imagen:
                    img_dev.append(imagen)
        
        print(img_dev)

        browser.close()

        
        print("\n--- RESULTADOS ---")

        print("\n--- COMPARACIÓN TITLE ---")

        if titulo_prod == titulo_dev:
            print("✅ Los títulos coinciden.")
        else:
            print(f"❌ Discrepancia en títulos:")
            print(f"   Prod: {titulo_prod}")
            print(f"   Dev:  {titulo_dev}")

        print("\n--- COMPARACIÓN DE H1 TITULO ---")

        if h1_prod == h1_dev:
            print(f"✅ Los H1 coinciden.")
        else:
            print(f"❌ Discrepancia en H1:")
            print(f"   Prod: {h1_prod}")
            print(f"   Dev:  {h1_dev}")

        print("\n--- COMPARACIÓN DE BREADCRUMB ---")

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

        print("\n--- COMPARACIÓN DE CATEGORÍAS ---")

        categorias_prod_clean = "".join(categorias_prod).replace(" ", "")
        categorias_dev_clean = "".join(categorias_dev).replace(" ", "")

        if categorias_dev == categorias_prod:
            print("✅ Los div de categoria coinciden.")
        else:
            print(f"❌ Discrepancia en div categoria:")
            print(f"   Prod: {categorias_prod_clean}")
            print(f"   Dev:  {categorias_dev_clean}")

        print("\n--- COMPARACIÓN DE MENÚ ---")

        if menu_dev == menu_prod:
            print("✅ Los elementos del div menú coinciden.")
        else:
            print(f"❌ Discrepancia en div menú: ")
            print(f"   Prod: {menu_prod}")
            print(f"   Dev:  {menu_dev}")
        
        print("\n--- COMPARACIÓN DE REFERENCIA ---")

        ref_clean_prod = ref_prod.replace("\n", " ",)
        if ref_dev == ref_clean_prod:
            print("✅ Los elementos de referencia coinciden.")
        else:
            print(f"❌ Discrepancia en referencia: ")
            print(f"   Prod: {ref_clean_prod}")
            print(f"   Dev:  {ref_dev}")
        
        print("\n--- COMPARACIÓN DE FABRICANTE ---")
        fabricante_str = "".join(fabricante_prod).replace(" ","")
        
        if fabricante_dev == fabricante_str:
            print("✅ Los elementos del fabricante coinciden.")
        else:
            print(f"❌ Discrepancia en el fabricante: ")
            print(f"   Prod: {fabricante_str}")
            print(f"   Dev:  {fabricante_dev}")
        
        print("\n--- COMPARACIÓN DE DESCRIPCIÓN ---")

        descripcion_prod_clean = "".join(descripcion_prod).replace(" ","")
        descripcion_dev_clean = descripcion_dev.replace(" ", "")
        if descripcion_dev_clean == descripcion_prod_clean:
            print("✅ Las descripciones coinciden.")
        else:
            print(f"❌ Discrepancia en la descripción: ")
            print(f"   Prod: {descripcion_prod_clean}")
            print(f"   Dev:  {descripcion_dev_clean}")
        
        print("\n--- COMPARACIÓN DE UDS/EMBALAJE ---")

        uds_prod_clean = "".join(uds_prod).replace(" ","")
        uds_dev_clean = "".join(uds_dev).replace(" ","")

        if uds_prod_clean == uds_dev_clean:
            print("✅ Las uds/embalaje coinciden.")
        else:
            print(f"❌ Discrepancia en uds/embalaje: ")
            print(f"   Prod: {uds_prod_clean}")
            print(f"   Dev:  {uds_dev_clean}")

        

if __name__ == "__main__":
    URL_PROD = "https://www.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    URL_DEV = "https://fo-dev.electricautomationnetwork.com/es/siemens/3na3124-6-3na31246-siemens-cartucho-fusible-nh-nh1-in-80-a-gg-un-ac-690-v-un-dc-440-v-indicador-de-fu"
    comparar_webs(URL_PROD, URL_DEV)
