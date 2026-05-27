import csv
import os
from datetime import datetime

import json
import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Cerrador Pro Enterprise",
    page_icon="💼",
    layout="wide"
)

# =========================================================
# ESTILOS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f4f6f8;
}

.box {
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 16px;
    background: white;
    box-shadow: 0 8px 20px rgba(0,0,0,0.05);
}

.aprobado {
    border-left: 6px solid #2ecc71;
    background: #eefaf1;
    color: #145a32;
}

.denegado {
    border-left: 6px solid #e74c3c;
    background: #fdecec;
    color: #78281f;
}

.comision {
    background: #fff8e1;
    padding: 20px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: bold;
    color: #7d6608;
}

.destino {
    background: #e8f8f5;
    padding: 12px;
    border-radius: 10px;
    color: #117864;
    margin-bottom: 10px;
    font-weight: bold;
}

.adminbox {
    background: #ebf5fb;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# ARCHIVOS
# =========================================================

SALES_FILE = "ventas.csv"
USERS_FILE = "usuarios.csv"
CLIENTS_FILE = "clientes.csv"
CONFIG_FILE = "config.json"

# =========================================================
# ESTADOS
# =========================================================

zonas = {
    "Alabama": "Costa Este",
    "Alaska": "Costa Oeste",
    "Arizona": "Costa Oeste",
    "Arkansas": "Zona Central",
    "California": "Costa Oeste",
    "North Carolina": "Costa Este",
    "South Carolina": "Costa Este",
    "Colorado": "Costa Oeste",
    "Connecticut": "Costa Este",
    "North Dakota": "Zona Central",
    "South Dakota": "Zona Central",
    "Delaware": "Costa Este",
    "Florida": "Costa Este",
    "Georgia": "Costa Este",
    "Hawaii": "Costa Oeste",
    "Idaho": "Costa Oeste",
    "Illinois": "Zona Central",
    "Indiana": "Zona Central",
    "Iowa": "Zona Central",
    "Kansas": "Zona Central",
    "Kentucky": "Zona Central",
    "Louisiana": "Zona Central",
    "Maine": "Costa Este",
    "Maryland": "Costa Este",
    "Massachusetts": "Costa Este",
    "Michigan": "Zona Central",
    "Minnesota": "Zona Central",
    "Mississippi": "Zona Central",
    "Missouri": "Zona Central",
    "Montana": "Costa Oeste",
    "Nebraska": "Zona Central",
    "Nevada": "Costa Oeste",
    "New Jersey": "Costa Este",
    "New York": "Costa Este",
    "New Hampshire": "Costa Este",
    "New Mexico": "Costa Oeste",
    "Ohio": "Zona Central",
    "Oklahoma": "Zona Central",
    "Oregon": "Costa Oeste",
    "Pennsylvania": "Costa Este",
    "Rhode Island": "Costa Este",
    "Tennessee": "Zona Central",
    "Texas": "Zona Central",
    "Utah": "Costa Oeste",
    "Vermont": "Costa Este",
    "Virginia": "Costa Este",
    "West Virginia": "Costa Este",
    "Washington": "Costa Oeste",
    "Wisconsin": "Zona Central",
    "Wyoming": "Costa Oeste"
}

horarios = {
    "Costa Oeste": "6 AM - 2 PM",
    "Zona Central": "7 AM - 4 PM",
    "Costa Este": "9 AM - 5 PM",
}

# =========================================================
# DESTINOS
# =========================================================

destinos_vdl = [
    "Cancún",
    "Punta Cana",
    "Puerto Vallarta",
    "Los Cabos",
    "Bahamas",
    "Costa Rica"
]

destinos_mix = [
    "Las Vegas",
    "Phoenix",
    "San Diego",
    "Los Ángeles",
    "Bahamas",
    "México"
]

hoteles = {
    "Cancún": [
        "Oasis Palm Lite",
        "Villa del Palmar"
    ],
    "Punta Cana": [
        "Ancora"
    ],
    "Las Vegas": [
        "Tuscany Suites"
    ],
    "Orlando": [
        "Avanti",
        "Buena Vista Suites"
    ]
}

cruceros = {
    "Miami": "Key West + Cozumel",
    "Port Canaveral": "Bahamas + Nassau",
    "Long Beach": "Ensenada + Islas Catalina",
    "New Orleans": "Cozumel + Progreso"
}

# =========================================================
# CREAR ARCHIVOS
# =========================================================

def crear_archivo(file, columnas):
    if not os.path.exists(file):
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas)

# Archivo de debug para eventos (no cambia datos de la app)
DEBUG_LOG = "app_debug.log"


def log_event(event, info=None):
    try:
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        entry = {"ts": now, "event": event, "info": info}
        with open(DEBUG_LOG, "a", encoding="utf-8") as df:
            df.write(json.dumps(entry, ensure_ascii=False) + "\n")
        st.session_state["last_event"] = entry
    except Exception:
        # no debemos interrumpir la app por logging
        pass

crear_archivo(
    SALES_FILE,
    [
        "Fecha",
        "Cliente",
        "Asesor",
        "Paquete",
        "Estado",
        "Edad",
        "Estado Civil",
        "Residencia",
        "Hijos",
        "Comisión"
    ]
)

crear_archivo(
    USERS_FILE,
    [
        "Usuario",
        "Password",
        "Rol"
    ]
)

crear_archivo(
    CLIENTS_FILE,
    [
        "Cliente",
        "Teléfono",
        "Seguimiento"
    ]
)

# =========================================================
# CONFIG JSON
# =========================================================

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cargar_config():
    default = {
        "horarios": horarios,
        "zonas": zonas,
        "porcentaje_default": 0.06,
        "reglas_calificacion": {
            "VDL": "Residente + Casado/Convive + hijos hasta 11 años",
            "HÍBRIDO": "Mujer Soltera, Divorciado o rango extendido",
            "MIX & MATCH": "Edad >= 18 y hijos hasta 17 años"
        }
    }
    config = load_json(CONFIG_FILE, default)
    config["horarios"] = config.get("horarios", horarios)
    config["zonas"] = config.get("zonas", zonas)
    config["porcentaje_default"] = config.get("porcentaje_default", 0.06)
    config["reglas_calificacion"] = config.get("reglas_calificacion", default["reglas_calificacion"])
    return config


def guardar_config(config):
    save_json(CONFIG_FILE, config)


CONFIG = cargar_config()
horarios = CONFIG.get("horarios", horarios)
zonas = CONFIG.get("zonas", zonas)

# =========================================================
# LOGIN
# =========================================================

DEFAULT_USERS = {
    "juanpablo": {"password": "asesor2026", "rol": "asesor", "name": "Juan Pablo"},
    "mariajose": {"password": "admin2026", "rol": "admin", "name": "María José"},
    "admin": {"password": "admin123", "rol": "admin", "name": "Administrador"},
    "asesor": {"password": "1234", "rol": "asesor", "name": "Asesor"},
}


def cargar_usuarios():
    usuarios = DEFAULT_USERS.copy()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Usuario"):
                    key = row["Usuario"].strip().lower()
                    usuarios[key] = {
                        "password": row.get("Password", ""),
                        "rol": row.get("Rol", "asesor"),
                        "name": row.get("Usuario", key)
                    }
    return usuarios


def guardar_usuarios():
    with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Usuario", "Password", "Rol"])
        for username, info in USERS.items():
            writer.writerow([
                username,
                info.get("password", ""),
                info.get("rol", "asesor")
            ])


USERS = cargar_usuarios()

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.session_state.name = ""

st.sidebar.title("🔐 Login")

usuario = st.sidebar.text_input("Usuario", key="login_usuario")
password = st.sidebar.text_input("Contraseña", type="password", key="login_password")

if st.sidebar.button("Ingresar", key="login_button"):
    usuario_key = usuario.strip().lower()
    usuario_info = USERS.get(usuario_key)
    if usuario_info and password == usuario_info["password"]:
        st.session_state.login = True
        st.session_state.usuario = usuario_key
        st.session_state.name = usuario_info.get("name", usuario_key)
        st.session_state.rol = usuario_info.get("rol", "asesor")
        log_event("login_success", {"usuario": usuario_key})
    else:
        st.sidebar.error("Usuario incorrecto")
        log_event("login_failed", {"usuario": usuario_key})

if not st.session_state.login:
    st.warning("Inicia sesión")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

menu_options = [
    "💰 Ventas",
    "📞 Clientes",
    "🏨 Hoteles",
    "📦 Paquetes"
]

if st.session_state.rol == "admin":
    menu_options = [
        "📊 Dashboard",
        "💰 Ventas",
        "📞 Clientes",
        "🏨 Hoteles",
        "📦 Paquetes",
        "📈 Estadísticas",
        "💵 Comisiones",
        "⚙️ Configuración"
    ]

menu = st.sidebar.radio(
    "Panel",
    menu_options,
    key="menu_panel"
)

admin_menu = None
if st.session_state.rol == "admin":
    admin_menu = st.sidebar.radio(
        "Admin",
        [
            "👥 Usuarios",
            "📜 Historial"
        ],
        key="admin_panel"
    )

# =========================================================
# VENTAS
# =========================================================

def hijos_validos_vdl(edades):
    return all(edad_hijo <= 11 for edad_hijo in edades)


def hijos_validos_mix(edades):
    return all(edad_hijo <= 17 for edad_hijo in edades)

# =========================================================
# DASHBOARD
# =========================================================

if menu == "📊 Dashboard":
    st.title("💼 Cerrador Pro Enterprise")

    if os.path.exists(SALES_FILE):
        ventas_df = pd.read_csv(SALES_FILE)
    else:
        ventas_df = pd.DataFrame()

    total_ventas = len(ventas_df)
    total_comisiones = 0
    if not ventas_df.empty and "Comisión" in ventas_df.columns:
        total_comisiones = ventas_df["Comisión"].astype(float).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas", total_ventas)
    col2.metric("Usuario", st.session_state.name)
    col3.metric("Rol", st.session_state.rol)
    st.markdown("---")
    st.write("Registro de ventas guardado en `ventas.csv` y clientes en `clientes.csv`.")
    st.metric("Comisión acumulada", f"${total_comisiones:,.2f}")

# =========================================================
# VENTAS
# =========================================================

if menu == "💰 Ventas":
    st.title("💰 Nueva Venta")

    cliente = st.text_input("Cliente", key="venta_cliente")

    estado = st.selectbox(
        "Estado",
        sorted(zonas.keys()),
        key="venta_estado"
    )

    estado_civil = st.selectbox(
        "Estado civil",
        [
            "Casado / Convive",
            "Mujer Soltera",
            "Hombre Soltero"
        ],
        key="venta_estado_civil"
    )

    edad = st.number_input(
        "Edad",
        18,
        100,
        30,
        key="venta_edad"
    )

    residencia = st.selectbox(
        "Residente o ciudadano",
        [
            "Sí",
            "No"
        ],
        key="venta_residencia"
    )

    cantidad_hijos = st.number_input(
        "Cantidad hijos",
        0,
        10,
        0,
        key="venta_cantidad_hijos"
    )

    edades_hijos = []
    if cantidad_hijos > 0:
        st.subheader("Edades hijos")
        for i in range(cantidad_hijos):
            edad_hijo = st.number_input(
                f"Edad hijo {i+1}",
                0,
                25,
                key=f"venta_hijo_{i}"
            )
            edades_hijos.append(edad_hijo)

    paquete = "MIX & MATCH"
    vigencia = "24 meses"
    beneficios = []
    destinos = []
    califica = False

    if residencia == "Sí":
        if estado_civil == "Casado / Convive":
            if 30 <= edad <= 70:
                if hijos_validos_vdl(edades_hijos):
                    paquete = "VDL"
                    vigencia = "12 meses reservar / 18 vacacionar"
                    beneficios = [
                        "All inclusive",
                        "3 comidas",
                        "Bebidas alcohólicas",
                        "Transporte aeropuerto-hotel",
                        "90 mins Time Share"
                    ]
                    destinos = destinos_vdl
                    califica = True
        elif estado_civil == "Mujer Soltera":
            if 25 <= edad <= 70:
                paquete = "HÍBRIDO"
                beneficios = [
                    "1 destino VDL",
                    "2 Mix & Match",
                    "90 mins Time Share"
                ]
                destinos = [
                    "Cancún",
                    "Las Vegas",
                    "Orlando"
                ]
                califica = True
        elif estado_civil == "Hombre Soltero":
            if 35 <= edad <= 59:
                paquete = "VDL"
                beneficios = [
                    "All inclusive",
                    "Hospedaje premium",
                    "Transporte incluido"
                ]
                destinos = [
                    "Puerto Vallarta",
                    "Los Cabos",
                    "Lake Havasu"
                ]
                califica = True

    if not califica:
        if edad >= 18:
            if hijos_validos_mix(edades_hijos):
                paquete = "MIX & MATCH"
                beneficios = [
                    "Sin Time Share",
                    "Open 4/3",
                    "Crucero 5/4",
                    "12 meses para reservar"
                ]
                destinos = destinos_mix

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Resultado")
        if paquete == "VDL":
            st.success(f"✅ CALIFICA PARA VDL — Vigencia: {vigencia}")
        elif paquete == "HÍBRIDO":
            st.success("✅ CALIFICA PARA HÍBRIDO")
        else:
            st.warning("⚠️ ENVIAR A MIX & MATCH")

        st.subheader("Beneficios")
        for beneficio in beneficios:
            st.write("✅", beneficio)

        st.subheader("Destinos recomendados")
        for destino in destinos:
            st.write("🌴", destino)

        st.subheader("Cruceros disponibles")
        for salida, ruta in cruceros.items():
            st.write(f"🚢 {salida} → {ruta}")

    with col2:
        zona = zonas[estado]
        st.subheader("Zona")
        st.info(f"Zona: {zona}\n\nHorario: {horarios[zona]}")

        deducible = st.number_input(
            "Deducible",
            200,
            500,
            399,
            key="venta_deducible"
        )

        porcentaje = st.selectbox(
            "Porcentaje comisión",
            [6, 8],
            key="venta_porcentaje"
        )

        comision = deducible * (porcentaje / 100)

        st.metric("Comisión estimada", f"${comision:,.2f}")

        if st.button("Registrar Venta", key="btn_registrar_venta"):
            try:
                with open(SALES_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        datetime.now().isoformat(sep=" ", timespec="seconds"),
                        cliente,
                        st.session_state.name,
                        paquete,
                        estado,
                        edad,
                        estado_civil,
                        residencia,
                        cantidad_hijos,
                        comision
                    ])
                st.success("Venta registrada correctamente")
                log_event("registrar_venta", {"cliente": cliente, "asesor": st.session_state.name, "paquete": paquete})
            except Exception as e:
                st.error("Error al registrar la venta")
                log_event("registrar_venta_error", {"error": str(e)})

# =========================================================
# CLIENTES
# =========================================================

if menu == "📞 Clientes":
    st.title("📞 Seguimiento Clientes")

    cliente = st.text_input("Cliente", key="cliente_nombre")
    telefono = st.text_input("Teléfono", key="cliente_telefono")
    seguimiento = st.selectbox(
        "Seguimiento",
        [
            "Interesado",
            "Llamada pendiente",
            "Venta cerrada",
            "No contestó"
        ],
        key="cliente_seguimiento"
    )

    if st.button("Guardar Cliente", key="btn_guardar_cliente"):
        try:
            with open(CLIENTS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    cliente,
                    telefono,
                    seguimiento
                ])
            st.success("Cliente guardado")
            log_event("guardar_cliente", {"cliente": cliente, "telefono": telefono, "seguimiento": seguimiento})
        except Exception as e:
            st.error("Error al guardar cliente")
            log_event("guardar_cliente_error", {"error": str(e)})

    if os.path.exists(CLIENTS_FILE):
        df = pd.read_csv(CLIENTS_FILE)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay clientes guardados aún.")

# =========================================================
# HOTELES
# =========================================================

if menu == "🏨 Hoteles":
    st.title("🏨 Hoteles y Resorts")
    for ciudad, lista in hoteles.items():
        st.subheader(ciudad)
        for hotel in lista:
            st.write("🏨", hotel)

# =========================================================
# PAQUETES
# =========================================================

if menu == "📦 Paquetes":
    st.title("📦 Paquetes")
    st.subheader("VDL")
    st.write("""
    • 3 destinos
    • All inclusive
    • Transporte aeropuerto-hotel
    • 90 mins Time Share
    • Bebidas incluidas
    """)
    st.subheader("HÍBRIDO")
    st.write("""
    • 1 destino VDL
    • 2 destinos Mix & Match
    • Time Share
    """)
    st.subheader("MIX & MATCH")
    st.write("""
    • Open 4/3
    • Crucero 5/4
    • 2 destinos
    • 12 meses reservar
    """)

# =========================================================
# ESTADÍSTICAS
# =========================================================

if menu == "📈 Estadísticas":
    st.title("📈 Estadísticas")
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        if not df.empty:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            ventas_totales = len(df)
            hoy = pd.Timestamp.now().normalize()
            ventas_hoy = df[df["Fecha"] >= hoy].shape[0]
            ingresos = df["Comisión"].astype(float).sum() if "Comisión" in df.columns else 0.0
            mejor_asesor = df["Asesor"].value_counts().idxmax() if not df["Asesor"].empty else "N/A"
            conversión = f"{(ventas_hoy / ventas_totales * 100):.1f}%" if ventas_totales else "0%"

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ventas totales", ventas_totales)
            col2.metric("Cierres del día", ventas_hoy)
            col3.metric("Dinero entrado", f"${ingresos:,.2f}")
            col4.metric("Mejor asesor", mejor_asesor)

            st.markdown("---")
            st.subheader("Desglose por asesor")
            asesor_data = (
                df.groupby("Asesor")["Comisión"].agg(["count", "sum"]).reset_index()
                .rename(columns={"count": "Ventas", "sum": "Comisión Total"})
            )
            st.dataframe(asesor_data, use_container_width=True)
            st.bar_chart(asesor_data.set_index("Asesor")["Ventas"])

            st.markdown("---")
            st.subheader("Ventas por fecha")
            daily = df.groupby(df["Fecha"].dt.date).size().reset_index(name="Ventas")
            daily.columns = ["Fecha", "Ventas"]
            st.line_chart(daily.set_index("Fecha"))
            st.markdown(f"**Porcentaje de conversión**: {conversión}")
        else:
            st.info("No hay ventas registradas aún.")
    else:
        st.info("No hay ventas registradas aún.")

# =========================================================
# COMISIONES
# =========================================================

if menu == "💵 Comisiones":
    st.title("💵 Comisiones")
    if os.path.exists(SALES_FILE):
        df = pd.read_csv(SALES_FILE)
        if not df.empty:
            df["Comisión"] = df["Comisión"].astype(float)
            total = df["Comisión"].sum()
            asesor_totales = (
                df.groupby("Asesor")["Comisión"].agg(["sum", "count"]).reset_index()
                .rename(columns={"sum": "Comisión Total", "count": "Ventas"})
            )
            st.metric("Comisión total", f"${total:,.2f}")
            st.subheader("Comisiones por asesor")
            st.dataframe(asesor_totales, use_container_width=True)
            st.subheader("Ventas individuales")
            st.dataframe(df[["Fecha", "Cliente", "Asesor", "Paquete", "Comisión"]], use_container_width=True)
        else:
            st.info("No hay ventas registradas aún.")
    else:
        st.info("No hay ventas registradas aún.")

# =========================================================
# CONFIGURACIÓN
# =========================================================

if menu == "⚙️ Configuración":
    st.title("⚙️ Configuración Empresa")
    st.subheader("Horarios por zona")
    nueva_horarios = {}
    for zona, hora in sorted(CONFIG["horarios"].items()):
        nueva_horarios[zona] = st.text_input(f"Horario {zona}", value=hora, key=f"config_hora_{zona}")

    st.subheader("Zonas comunes")
    zonas_text = st.text_area(
        "Mapa de zonas (estado: zona)",
        value=json.dumps(CONFIG["zonas"], ensure_ascii=False, indent=2),
        height=220,
        key="config_zonas"
    )

    st.subheader("Porcentaje de comisión por defecto")
    porcentaje_def = st.number_input(
        "Porcentaje (%)",
        0.0,
        100.0,
        value=CONFIG.get("porcentaje_default", 0.06) * 100,
        key="config_porcentaje_default"
    )

    st.subheader("Reglas de calificación")
    reglas = CONFIG["reglas_calificacion"]
    regla_vdl = st.text_area("VDL", value=reglas.get("VDL", ""), key="config_regla_vdl")
    regla_hibrido = st.text_area("HÍBRIDO", value=reglas.get("HÍBRIDO", ""), key="config_regla_hibrido")
    regla_mix = st.text_area("MIX & MATCH", value=reglas.get("MIX & MATCH", ""), key="config_regla_mix")

    if st.button("Guardar configuración", key="config_guardar"):
        CONFIG["horarios"] = nueva_horarios
        try:
            CONFIG["zonas"] = json.loads(zonas_text)
        except json.JSONDecodeError:
            st.error("Zona mapping debe ser JSON válido")
            log_event("config_error", {"error": "zonas JSON inválido"})
        else:
            CONFIG["porcentaje_default"] = porcentaje_def / 100
            CONFIG["reglas_calificacion"] = {
                "VDL": regla_vdl,
                "HÍBRIDO": regla_hibrido,
                "MIX & MATCH": regla_mix
            }
            guardar_config(CONFIG)
            st.success("Configuración guardada")
            log_event("guardar_config", {"porcentaje_default": CONFIG.get("porcentaje_default")})

    st.markdown("---")
    st.write("La configuración se guarda en `config.json`. No se cambia la información de venta, solo la forma en que se presentan horarios y reglas.")

# =========================================================
# ADMIN USUARIOS
# =========================================================

if st.session_state.rol == "admin":
    if admin_menu == "👥 Usuarios":
        st.title("👥 Usuarios")
        st.markdown("**Usuarios existentes**")
        usuarios_list = [
            {"Usuario": username, "Rol": info.get("rol", "asesor")}
            for username, info in USERS.items()
        ]
        st.dataframe(pd.DataFrame(usuarios_list), use_container_width=True)

        st.markdown("---")
        st.subheader("Crear o actualizar usuario")
        nuevo_usuario = st.text_input("Usuario", key="new_user")
        nueva_pass = st.text_input("Contraseña", type="password", key="new_user_password")
        rol_usuario = st.selectbox(
            "Rol",
            [
                "admin",
                "asesor"
            ],
            key="new_user_rol"
        )
        if st.button("Guardar usuario", key="btn_guardar_usuario"):
            if not nuevo_usuario:
                st.error("Ingrese un nombre de usuario")
            else:
                USERS[nuevo_usuario.strip().lower()] = {
                    "password": nueva_pass,
                    "rol": rol_usuario,
                    "name": nuevo_usuario.strip()
                }
                guardar_usuarios()
                st.success("Usuario guardado")
                log_event("guardar_usuario", {"usuario": nuevo_usuario.strip().lower(), "rol": rol_usuario})

        st.markdown("---")
        st.subheader("Modificar usuario")
        usuario_seleccionado = st.selectbox(
            "Seleccionar usuario",
            sorted(USERS.keys()),
            key="select_usuario"
        )
        if usuario_seleccionado:
            datos = USERS[usuario_seleccionado]
            st.write(f"Rol actual: {datos.get('rol')}")
            nueva_rol = st.selectbox(
                "Nuevo rol",
                ["admin", "asesor"],
                index=0 if datos.get("rol") == "admin" else 1,
                key="modify_user_role"
            )
            nueva_clave = st.text_input("Nueva contraseña", type="password", key="modify_user_password")
            if st.button("Actualizar usuario", key="btn_actualizar_usuario"):
                if nueva_clave:
                    USERS[usuario_seleccionado]["password"] = nueva_clave
                USERS[usuario_seleccionado]["rol"] = nueva_rol
                guardar_usuarios()
                st.success("Usuario actualizado")
                log_event("actualizar_usuario", {"usuario": usuario_seleccionado, "new_rol": nueva_rol})
            if usuario_seleccionado != st.session_state.usuario:
                if st.button("Eliminar usuario", key="btn_eliminar_usuario"):
                    USERS.pop(usuario_seleccionado, None)
                    guardar_usuarios()
                    st.success("Usuario eliminado")
                    log_event("eliminar_usuario", {"usuario": usuario_seleccionado})
            else:
                st.info("No puede eliminar su propia cuenta.")

    if admin_menu == "📜 Historial":
        st.title("📜 Historial Completo")
        if os.path.exists(SALES_FILE):
            ventas = pd.read_csv(SALES_FILE)
            st.dataframe(ventas, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún.")
