import csv
import os
from datetime import datetime

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
                        "name": row.get("Usuario", row.get("Usuario", key))
                    }
    return usuarios

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
    else:
        st.sidebar.error("Usuario incorrecto")

if not st.session_state.login:
    st.warning("Inicia sesión")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

menu = st.sidebar.radio(
    "Panel",
    [
        "📊 Dashboard",
        "💰 Ventas",
        "📞 Clientes",
        "🏨 Hoteles",
        "📦 Paquetes",
        "📈 Estadísticas",
        "💵 Comisiones",
        "⚙️ Configuración"
    ],
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
            st.markdown(f"""
            <div class="box aprobado">
            ✅ CALIFICA PARA VDL

            <br><br>
            Vigencia:
            {vigencia}
            </div>
            """, unsafe_allow_html=True)
        elif paquete == "HÍBRIDO":
            st.markdown(f"""
            <div class="box aprobado">
            ✅ CALIFICA PARA HÍBRIDO
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="box denegado">
            ⚠️ ENVIAR A MIX & MATCH
            </div>
            """, unsafe_allow_html=True)

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

        st.markdown(f"""
        <div class="comision">
        Comisión:
        ${comision:,.2f}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Registrar Venta", key="btn_registrar_venta"):
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
        with open(CLIENTS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                cliente,
                telefono,
                seguimiento
            ])
        st.success("Cliente guardado")

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
        st.markdown(f"""
        <div class="destino">
        {ciudad}
        </div>
        """, unsafe_allow_html=True)
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
        st.dataframe(df, use_container_width=True)
        st.metric("Ventas Totales", len(df))
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
            total = df["Comisión"].astype(float).sum()
            st.metric(
                "Total Comisiones",
                f"${total:,.2f}"
            )
        else:
            st.info("No hay ventas registradas aún.")
    else:
        st.info("No hay ventas registradas aún.")

# =========================================================
# CONFIGURACIÓN
# =========================================================

if menu == "⚙️ Configuración":
    st.title("⚙️ Configuración Empresa")
    st.json(horarios)

# =========================================================
# ADMIN USUARIOS
# =========================================================

if st.session_state.rol == "admin":
    if admin_menu == "👥 Usuarios":
        st.title("👥 Usuarios")
        nuevo_usuario = st.text_input("Nuevo usuario", key="new_user")
        nueva_pass = st.text_input("Nueva contraseña", type="password", key="new_user_password")
        rol = st.selectbox(
            "Rol",
            [
                "admin",
                "asesor"
            ],
            key="new_user_rol"
        )
        if st.button("Crear Usuario", key="btn_crear_usuario"):
            with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    nuevo_usuario,
                    nueva_pass,
                    rol
                ])
            st.success("Usuario creado")
        if os.path.exists(USERS_FILE):
            usuarios = pd.read_csv(USERS_FILE)
            st.dataframe(usuarios)
    if admin_menu == "📜 Historial":
        st.title("📜 Historial Completo")
        if os.path.exists(SALES_FILE):
            ventas = pd.read_csv(SALES_FILE)
            st.dataframe(ventas, use_container_width=True)
        else:
            st.info("No hay ventas registradas aún.")
