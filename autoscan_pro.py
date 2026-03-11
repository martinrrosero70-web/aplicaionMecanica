import flet as ft


ft
import sqlite3
from datetime import datetime
import time
import random

def db_init():
    conn = sqlite3.connect("diagnostico_automotriz.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS escaneos 
                     (id INTEGER PRIMARY KEY, fecha TEXT, componente TEXT, estado TEXT, detalle TEXT)''')
    conn.commit()
    conn.close()

def guardar_escaneo(componente, estado, detalle):
    conn = sqlite3.connect("diagnostico_automotriz.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO escaneos (fecha, componente, estado, detalle) VALUES (?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), componente, estado, detalle))
    conn.commit()
    conn.close()

def main(page: ft.Page):
    # Configuración de página principal
    page.title = "AutoScan Pro - Diagnóstico Automotriz"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.bgcolor = "#0f172a" # Color de fondo oscuro y moderno (Slate 900)
    page.theme = ft.Theme(font_family="Segoe UI")
    
    # Base de conocimientos de fallas para simular un escaneo de OBD-II
    componentes = [
        {"nombre": "Motor", "icono": ft.icons.SETTINGS_APPLICATIONS, "fallas": ["Presión de aceite baja", "Bujías muy desgastadas", "Temperatura elevada", "Problema en inyectores"]},
        {"nombre": "Frenos", "icono": ft.icons.ERROR, "fallas": ["Pastillas desgastadas", "Líquido de frenos bajo", "Discos alabeados", "Aire en el sistema"]},
        {"nombre": "Batería", "icono": ft.icons.BATTERY_ALERT, "fallas": ["Voltaje muy bajo", "Alternador en mal estado", "Terminales sulfatados", "Celdas dañadas"]},
        {"nombre": "Transmisión", "icono": ft.icons.SETTINGS, "fallas": ["Nivel de aceite bajo", "Filtro obstruido", "Sobrecalentamiento", "Patines en engranajes"]},
        {"nombre": "Neumáticos", "icono": ft.icons.RADIO_BUTTON_UNCHECKED, "fallas": ["Presión crítica", "Desgaste irregular", "Pinchazo detectado", "Vida útil agotada"]},
        {"nombre": "Suspensión", "icono": ft.icons.BUILD, "fallas": ["Amortiguadores con fugas", "Bujes desgastados", "Resortes vencidos", "Bieletas rotas"]}
    ]

    lbl_ultimo_escaneo = ft.Text("Último escaneo: Nunca", size=14, color="#94a3b8")
    
    # Encabezado (Header)
    header = ft.Row(
        controls=[
            ft.Icon(ft.icons.DIRECTIONS_CAR, size=40, color="#38bdf8"), # Celeste
            ft.Text("AutoScan Pro", size=32, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(expand=True),
            lbl_ultimo_escaneo
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    lbl_status = ft.Text("Sistema listo para escanear componentes.", size=16, color="#cbd5e1")
    progress_bar = ft.ProgressBar(width=400, color="#38bdf8", bgcolor="#334155", visible=False)
    
    # Grilla para los resultados
    results_grid = ft.GridView(
        expand=1,
        runs_count=5, # Máximo número de elementos por fila (se adapta)
        max_extent=350, # Ancho máximo para que sean tarjetas anchas
        child_aspect_ratio=1.5,
        spacing=20,
        run_spacing=20,
    )

    def crear_tarjeta_resultado(nombre_comp, icono, estado, detalle):
        # Determinar colores y mensajes según el estado del componente
        if estado == "OK":
            color = "#10b981" # Verde Esmeralda (Buen Estado)
            bg_color = "#022c22"
            icon_color = "#34d399"
            status_text = "ÓPTIMO - BIEN"
        elif estado == "WARNING":
            color = "#f59e0b" # Amarillo Ámbar (Por Dañarse)
            bg_color = "#451a03"
            icon_color = "#fbbf24"
            status_text = "POR DAÑARSE (REVISAR)"
        else:
            color = "#ef4444" # Rojo (Dañado/Cambiar)
            bg_color = "#450a0a"
            icon_color = "#f87171"
            status_text = "DAÑADO - CAMBIAR AHORA"

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(icono, size=30, color=icon_color),
                        ft.Text(status_text, color=color, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(nombre_comp, size=22, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Container(expand=True),
                    ft.Text(detalle, size=14, color="#cbd5e1", no_wrap=False)
                ]
            ),
            padding=20,
            bgcolor=bg_color,
            border_radius=15,
            border=ft.border.all(1, color),
            animate=ft.animation.Animation(300, "easeOut")
        )

    def iniciar_escaneo(e):
        # UI durante el escaneo
        btn_scan.disabled = True
        progress_bar.visible = True
        progress_bar.value = 0
        lbl_status.value = "Conectando con ECU y sensores del vehículo..."
        results_grid.controls.clear()
        page.update()

        time.sleep(1)
        lbl_status.value = "Interrogando estado de componentes físicos..."
        page.update()

        # Animación de la barra de progreso
        for i in range(1, 101, 2):
            progress_bar.value = i * 0.01
            time.sleep(0.04)
            page.update()

        lbl_status.value = "Análisis completado exitosamente."
        progress_bar.visible = False
        
        # Generar resultados del escaneo para cada componente
        for comp in componentes:
            rand_val = random.random()
            
            # 50% probabilidad de que esté óptimo, 30% que esté por dañarse, 20% dañado
            if rand_val < 0.5:
                estado = "OK"
                detalle = "Parámetros dentro de especificaciones de fábrica. Ninguna acción requerida."
            elif rand_val < 0.8:
                estado = "WARNING"
                detalle = "Desgaste detectado: " + random.choice(comp["fallas"]) + ". Agendar cita para mantenimiento preventivo pronto."
            else:
                estado = "CRITICAL"
                detalle = "Falla crítica o final de vida útil: " + random.choice(comp["fallas"]) + ". Inmovilizar vehículo y cambiar componente."
            
            # Se guarda en DB
            guardar_escaneo(comp["nombre"], estado, detalle)
            # Se agrega la tarjeta a la UI
            results_grid.controls.append(crear_tarjeta_resultado(comp["nombre"], comp["icono"], estado, detalle))

        btn_scan.disabled = False
        lbl_ultimo_escaneo.value = f"Último escaneo: {datetime.now().strftime('%H:%M:%S')}"
        page.update()

    btn_scan = ft.ElevatedButton(
        content=ft.Row([ft.Icon(ft.icons.SEARCH), ft.Text("Iniciar Escaneo Computarizado", size=16, weight="bold")]),
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#0ea5e9",
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=iniciar_escaneo
    )

    # Contenedor principal que agrupa todo
    main_column = ft.Column(
        controls=[
            header,
            ft.Divider(height=30, color="#334155"),
            ft.Container(
                content=ft.Column([
                    ft.Text("Módulo de Diagnóstico Automotriz", size=20, weight="bold", color="#e2e8f0"),
                    ft.Text("Presione el botón para iniciar la lectura y conocer qué componentes están bien, por dañarse o deben cambiarse.", color="#94a3b8"),
                    ft.Container(height=10),
                    ft.Row([btn_scan, progress_bar], spacing=20, alignment=ft.MainAxisAlignment.START),
                    lbl_status,
                ]),
                bgcolor="#1e293b", # Slate 800
                padding=20,
                border_radius=10,
                border=ft.border.all(1, "#334155")
            ),
            ft.Container(height=20),
            ft.Text("Resultados del Estado de Componentes:", size=22, weight="bold", color="white"),
            results_grid
        ],
        expand=True
    )

    page.add(main_column)

if __name__ == '__main__':
    db_init()
    # Ejecutamos la app en modo web por el puerto 8550
    print("Iniciando servidor web. Ingresa a: http://localhost:8550")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
