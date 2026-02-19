import webbrowser
import os

def generar_html(datos):
    # Errores totales
    total_errores = sum(1 for x in datos['caja'] + datos['categorias'] + 
                        datos['etim'] + datos['menu'] + datos['busqueda'] +
                        datos['imagen']
                        if "❌" in x['estado'])
        
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe de Comparación QA</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #f4f7f6; }}
            h1 {{  padding: 12px; border: 1px solid #ddd; background-color: #007677; color: white; text-align: center;}}
            h2 {{ color: #333; }}
            .contenedor {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #fff; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #007677; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .ok {{ color: #28a745; font-weight: bold; background-color: #d4f7d4;}}
            .error {{ color: #dc3545; font-weight: bold; background-color: #fff5f5; }}
            .url-info {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
            .num-errores {{ padding: 15px; margin-bottom: 20px; border-radius: 5px; font-weight: bold; }}
            .suma-error {{ background-color: #ffdce0; color: #af192b; border: 1px solid #af192b; }}
            .suma-ok {{ background-color: #dcffe4; color: #155724; border: 1px solid #155724; }}
        </style>
    </head>
    <body>
        <div class="contenedor">
            <h1>Comparador Regresión EAN</h1>
            <div class="num-errores {'suma-error' if total_errores > 0 else 'suma-ok'}">
                Se han encontrado {total_errores} diferencias en la comparación.
            </div>
            <div class="url-info">
                <p><strong>PROD:</strong> <a href="{datos['url_prod']}">{datos['url_prod']}</a></p>
                <p><strong>DEV:</strong> <a href="{datos['url_dev']}">{datos['url_dev']}</a></p>
            </div>

            <h2>SEO </h2>
            <table>
                <thead>
                    <tr>
                        <th>Elemento</th>
                        <th>Producción</th>
                        <th>Desarrollo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Meta Title</strong></td>
                        <td>{datos['title']['prod']}</td>
                        <td>{datos['title']['dev']}</td>
                        <td>{'✅' if datos['title']['prod'] == datos['title']['dev'] else '❌'}</td>
                    </tr>
                    <tr>
                        <td><strong>H1 Principal</strong></td>
                        <td>{datos['h1']['prod']}</td>
                        <td>{datos['h1']['dev']}</td>
                        <td>{'✅' if datos['h1']['prod'] == datos['h1']['dev'] else '❌'}</td>
                    </tr>
                    <tr>
                        <td><strong>Breadcrumb</strong></td>
                        <td>{datos['breadcrumb']['prod']}</td>
                        <td>{datos['breadcrumb']['dev']}</td>
                        <td>{'✅' if datos['breadcrumb']['prod'].strip() == datos['breadcrumb']['dev'].strip() else '❌'}</td>
                    </tr>
                </tbody>
            </table>
            
            <h2>Imágenes Producto</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>PROD (Cantidad)</th>
                        <th>DEV (Cantidad)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    for item in datos['imagen']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['imagen_p']}</td>
                        <td>{item['imagen_d']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>
                """
        
    html+= """
                </tbody>
            </table>
           
            
            <h2>Menú de Navegación</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>PROD (Botón)</th>
                        <th>DEV (Botón)</th>
                        <th>PROD (Enlace)</th>
                        <th>DEV (Enlace)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""

    for item in datos['menu']:
        clase = "ok" if "✅" in item['estado'] else "error"
                
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['texto_p']}</td>
                        <td>{item['texto_d']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_p']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_d']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""       

    html += """
                </tbody>
            </table>

            <h2>Contenedor de Compra y Precios</h2>
            <table>
                <thead>
                    <tr>
                        <th>Campo</th>
                        <th>Producción</th>
                        <th>Desarrollo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for item in datos['caja']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['campo']}</td>
                        <td>{item['prod']}</td>
                        <td>{item['dev']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>

            <h2>Referencias, Fabricante y Descripción corta y larga</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>Producción</th>
                        <th>Desarrollo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for item in datos['referencias']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['prod']}</td>
                        <td>{item['dev']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>



            <h2>Categorías </h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>Producción</th>
                        <th>Desarrollo</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for item in datos['categorias']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['prod']}</td>
                        <td>{item['dev']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>

            <h2>Enlace Garantía, reparación y devolución</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>PROD (Texto)</th>
                        <th>DEV (Texto)</th>
                        <th>PROD (Enlace)</th>
                        <th>DEV (Enlace)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""

    for item in datos['garantia']:
        clase = "ok" if "✅" in item['estado'] else "error"
                
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['texto_p']}</td>
                        <td>{item['texto_d']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_p']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_d']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""       

    html += """
                </tbody>
            </table>

            <h2>Más Info, PDF y Opiniones</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>PROD (Texto)</th>
                        <th>DEV (Texto)</th>
                        <th>PROD (Enlace)</th>
                        <th>DEV (Enlace)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""

    for item in datos['masinfo']:
        clase = "ok" if "✅" in item['estado'] else "error"
                
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['texto_p']}</td>
                        <td>{item['texto_d']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_p']}</td>
                        <td style="font-size: 0.8em; color: #666; max-width: 200px; word-break: break-all;">{item['url_d']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""       

    html += """
                </tbody>
            </table>


            <h2>Características Técnicas (ETIM)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Índice</th>
                        <th>PROD (Característica)</th>
                        <th>PROD (Valor+Unidad)</th>
                        <th>DEV (Característica)</th>
                        <th>DEV (Valor+Unidad)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for item in datos['etim']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['indice']}</td>
                        <td>{item['nombre_p']}</td>
                        <td>{item['valor_p']} {item['unidad_p']}</td>
                        <td>{item['nombre_d']}</td>
                        <td>{item['valor_d']} {item['unidad_d']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>
            
            <h2>Búsqueda de Productos (Buscador)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Posición</th>
                        <th>PROD (Referencia)</th>
                        <th>DEV (Referencia)</th>
                        <th>PROD (Título)</th>
                        <th>DEV (Título)</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for item in datos['busqueda']:
        clase = "ok" if "✅" in item['estado'] else "error"
        html += f"""
                    <tr>
                        <td>{item['posicion']}</td>
                        <td>{item['prod_ref']}</td>
                        <td>{item['dev_ref']}</td>
                        <td>{item['prod_titulo']}</td>
                        <td>{item['dev_titulo']}</td>
                        <td class="{clase}">{item['estado']}</td>
                    </tr>"""

    html += """
                </tbody>
            </table>
            
        </div>
    </body>
    </html>
    """

    # Guardar el archivo, hay que importat unas librerías específicas
    with open("reporte_qa.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\n✅ Informe HTML generado con éxito: reporte_qa.html")
    
    ruta_archivo = os.path.abspath("reporte_qa.html")
    webbrowser.open(f"file://{ruta_archivo}")
