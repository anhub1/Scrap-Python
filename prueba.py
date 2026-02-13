
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def ejecutar_prueba():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Ir a la web de producción
        page.goto("https://google.com")
        page.screenshot(path="prod.png")
        
        # Analizar el HTML con BeautifulSoup
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        print(f"Título encontrado: {soup.title.string}")
        
        browser.close()

if __name__ == "__main__":
    ejecutar_prueba()
