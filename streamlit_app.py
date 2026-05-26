import csv
import os
from datetime import datetime

import streamlit as st
import json

# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------

st.set_page_config(
    page_title="Cerrador Pro",
    page_icon="💼",
    layout="wide"
)

USERS = {
    "juanpablo": {
        "name": "Juan Pablo",
        "role": "asesor",
        "password": "asesor2026"
    },
    "mariajose": {
        "name": "María José",
        "role": "admin",
        "password": "admin2026"
    }
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["user_fullname"] = ""
    st.session_state["role"] = ""
    st.session_state["message"] = ""

if not st.session_state["authenticated"]:
    st.title("Iniciar sesión")
    username_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        username_key = username_input.strip().lower()
        user = USERS.get(username_key)
        if user and password_input == user["password"]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_key
            st.session_state["user_fullname"] = user["name"]
            st.session_state["role"] = user["role"]
            st.session_state["message"] = f"Bienvenido {user['name']}"
        else:
            st.error("Usuario o contraseña incorrectos.")
    if not st.session_state["authenticated"]:
        st.stop()

# -----------------------------------
# BASE DE DATOS
# -----------------------------------

zonas = {
    "Alabama": "Costa Este",
    "Alaska": "Costa Oeste",
    "Arizona": "Costa Oeste",
    "Arkansas": "Zona Central",
    "California": "Costa Oeste",
    "Colorado": "Zona Central",
    "Connecticut": "Costa Este",
    "Delaware": "Costa Este",
    "Florida": "Costa Este",
}

# Archivo de ventas y campos
SALES_FILE = "sales_records.csv"
FIELDNAMES = [
    "timestamp",
    "cliente",
    "estado",
    "estado_civil",
    "edad",
    "residencia",
    "zona",
    "destino",
    "hotel",
    "paquete",
    "vigencia",
    "deducible",
    "comision",
    "ventas",
    "ganancia_unitaria",
    "total",
    "cantidad_hijos",
    "edades_hijos",
    "beneficios",
    "destinos_recomendados",
    "cruceros_recomendados",
    "asesor",
]


def ensure_sales_file():
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


# Persistencia simple para usuarios, hoteles, paquetes y seguimiento
USERS_FILE = "users.json"
HOTELES_FILE = "hoteles.json"
PACKAGES_FILE = "packages.json"
CONFIG_FILE = "config.json"
FOLLOWUPS_FILE = "followups.json"


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    else:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Hoteles de ejemplo por ciudad
hoteles = {
    "Cancún": ["Hotel Azul", "Resort Playa"],
    "Punta Cana": ["Resort Caribe"],
    "Puerto Vallarta": ["Hotel Pacifico"],
}

# Horarios por zona
horarios = {
    "Costa Este": "9:00 - 18:00",
    "Costa Oeste": "8:00 - 17:00",
    "Zona Central": "8:30 - 17:30",
}


# Cargar o inicializar datos persistentes
USERS = load_json(USERS_FILE, USERS)
hoteles = load_json(HOTELES_FILE, hoteles)
PACKAGES = load_json(PACKAGES_FILE, {
    "VDL": {
        "vigencia": "12 meses reservar / 18 vacacionar",
        "requisitos": "Residente, Casado/Convive, edades permitidas",
    },
    "HÍBRIDO": {
        "vigencia": "12 meses reservar / 18 vacacionar",
        "requisitos": "Mujer soltera o divorciado, rango de edad",
    },
    "MIX & MATCH": {
        "vigencia": "12 meses para reservar / 18 vacacionar",
        "requisitos": "Edad >=18, hijos hasta 17",
    }
})

CONFIG = load_json(CONFIG_FILE, {
    "horarios": horarios,
    "zonas": zonas,
    "porcentaje_default": 0.06,
})

FOLLOWUPS = load_json(FOLLOWUPS_FILE, [])


def persist_users():
    save_json(USERS_FILE, USERS)


def persist_hoteles():
    save_json(HOTELES_FILE, hoteles)


def persist_packages():
    save_json(PACKAGES_FILE, PACKAGES)


def persist_config():
    save_json(CONFIG_FILE, CONFIG)


def persist_followups():
    save_json(FOLLOWUPS_FILE, FOLLOWUPS)


def load_sales():
    ensure_sales_file()
    with open(SALES_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_sale(record):
    ensure_sales_file()
    with open(SALES_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(record)


def hijos_validos_vdl(edades):
    for edad_hijo in edades:
        if edad_hijo > 11:
            return False
    return True


def hijos_validos_mix(edades):
    for edad_hijo in edades:
        if edad_hijo > 17:
            return False
    return True


def compute_package(
    estado_civil,
    edad,
    residencia,
    cantidad_hijos,
    edades_hijos
):
    # Valores por defecto
    califica = False
    paquete = "MIX & MATCH"
    vigencia = "24 meses"
    motivo = "No cumple los requisitos"
    beneficios = []
    destinos_recomendados = []
    cruceros_recomendados = []

    # Helpers locales
    residencia_flag = (residencia == "Sí")

    # Reglas para residentes
    if residencia_flag:
        if estado_civil == "Casado / Convive":
            # Rango de edad permitido para VDL y validación de hijos
            if 25 <= edad <= 79 and hijos_validos_vdl(edades_hijos):
                califica = True
                paquete = "VDL"
                vigencia = "12 meses reservar / 18 vacacionar"
                beneficios = [
                    "All inclusive",
                    "3 comidas incluidas",
                    "Bebidas alcohólicas y no alcohólicas",
                    "Transporte aeropuerto-hotel",
                    "90 min Time Share sin compromiso"
                ]
                destinos_recomendados = [
                    "Cancún",
                    "Punta Cana",
                    "Puerto Vallarta",
                    "Los Cabos",
                    "Bahamas",
                    "Costa Rica"
                ]
                cruceros_recomendados = [
                    "Crucero Caribe 5N/4D",
                    "Crucero Riviera Maya 7N/6D"
                ]

        if estado_civil == "Mujer Soltera":
            if 25 <= edad <= 72:
                califica = True
                paquete = "HÍBRIDO"
                vigencia = "12 meses reservar / 18 vacacionar"
                beneficios = [
                    "1 destino VDL",
                    "2 destinos Mix & Match",
                    "Time Share 90 minutos"
                ]
                destinos_recomendados = [
                    "Cancún",
                    "Vegas",
                    "Orlando"
                ]
                cruceros_recomendados = [
                    "Crucero Bahamas 5N/4D",
                    "Crucero Panamá 8N/7D"
                ]

        if estado_civil == "Hombre Soltero":
            if 35 <= edad <= 59:
                califica = True
                paquete = "VDL"
                vigencia = "12 meses reservar / 18 vacacionar"
                beneficios = [
                    "All inclusive",
                    "Hospedaje premium",
                    "Transporte incluido"
                ]
                destinos_recomendados = [
                    "Puerto Vallarta",
                    "Los Cabos",
                    "Lake Havasu"
                ]
                cruceros_recomendados = [
                    "Crucero Caribe 5N/4D",
                    "Crucero Bahía Mar 6N/5D"
                ]

        if estado_civil == "Divorciado":
            if 25 <= edad <= 72:
                califica = True
                paquete = "HÍBRIDO"
                vigencia = "12 meses reservar / 18 vacacionar"
                beneficios = [
                    "1 destino VDL",
                    "2 destinos Mix & Match",
                    "Time Share 90 minutos"
                ]
                destinos_recomendados = [
                    "Cancún",
                    "Vegas",
                    "Orlando"
                ]
                cruceros_recomendados = [
                    "Crucero Bahamas 5N/4D"
                ]

    # Si no calificó para paquetes preferenciales o no es residente
    if not califica:
        # Reglas generales para MIX & MATCH: edad mínima y validación de hijos
        if edad >= 18 and hijos_validos_mix(edades_hijos):
            paquete = "MIX & MATCH"
            vigencia = "12 meses para reservar / 18 vacacionar"
            beneficios = [
                "Sin Time Share",
                "Open 4/3",
                "Crucero 5/4",
                "12 meses para reservar",
                "2 destinos"
            ]
            destinos_recomendados = [
                "Bahamas",
                "México",
                "Las Vegas",
                "Phoenix",
                "Los Ángeles",
                "San Diego"
            ]
            cruceros_recomendados = [
                "Crucero Bahamas 5N/4D",
                "Crucero Miami 4N/3D"
            ]
        else:
            motivo = "No cumple los requisitos de edad o hijos para ningún paquete"

    return (
        califica,
        paquete,
        vigencia,
        motivo,
        beneficios,
        destinos_recomendados,
        cruceros_recomendados
    )


def parse_edades_hijos(edades_str):
    if edades_str is None:
        return []

    edades_str = edades_str.strip()
    if edades_str == "":
        return []

    edades = []
    for part in edades_str.split(","):
        part = part.strip()
        if part == "":
            continue

        try:
            edad = int(part)
        except ValueError:
            return None

        if edad < 0 or edad > 25:
            return None

        edades.append(edad)

    return edades


def reset_form():
    st.session_state["cliente"] = ""
    st.session_state["estado"] = "Alabama"
    st.session_state["estado_civil"] = "Casado / Convive"
    st.session_state["edad"] = 35
    st.session_state["residencia"] = "Sí"
    st.session_state["porcentaje"] = 6
    st.session_state["ventas"] = 1
    st.session_state["deducible"] = 399
    st.session_state["cantidad_hijos"] = 0
    st.session_state["edades_hijos_str"] = ""
    st.session_state["message"] = ""
    st.session_state["sale_registered"] = False
    st.session_state["show_records"] = False

if "cliente" not in st.session_state:
    reset_form()

if "message" not in st.session_state:
    st.session_state["message"] = ""

if "sale_registered" not in st.session_state:
    st.session_state["sale_registered"] = False

if "show_records" not in st.session_state:
    st.session_state["show_records"] = False

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Datos del cliente")

st.sidebar.write(f"Asesor: {st.session_state['user_fullname']}")

cliente = st.sidebar.text_input("Nombre del cliente", key="cliente")

estado = st.sidebar.selectbox(
    "Estado",
    sorted(list(zonas.keys())),
    key="estado"
)

estado_civil = st.sidebar.selectbox(
    "Estado civil",
    [
        "Casado / Convive",
        "Mujer Soltera",
        "Hombre Soltero",
        "Divorciado"
    ],
    key="estado_civil"
)

edad = st.sidebar.number_input(
    "Edad",
    18,
    100,
    key="edad"
)

residencia = st.sidebar.selectbox(
    "Residente USA/Canadá?",
    ["Sí", "No"],
    key="residencia"
)

deducible = st.sidebar.number_input(
    "Monto deducible",
    150,
    500,
    399,
    key="deducible"
)

st.sidebar.markdown("---")

st.sidebar.markdown("Vista principal con todos los hoteles disponibles por ciudad.")

porcentaje = st.sidebar.radio(
    "Comisión (%)",
    [6, 8],
    index=0,
    key="porcentaje"
) / 100

ventas = 1
st.sidebar.markdown("Solo se puede vender 1 paquete por registro.")

st.sidebar.markdown("---")

cantidad_hijos = st.sidebar.number_input(
    "Cantidad de hijos",
    0,
    10,
    key="cantidad_hijos"
)

edades_hijos_str = st.sidebar.text_input(
    "Edades de los hijos (separadas por coma)",
    key="edades_hijos_str",
    help="Ejemplo: 5, 8, 12"
)

edades_hijos = parse_edades_hijos(edades_hijos_str)
edades_hijos_invalid = edades_hijos is None
if edades_hijos_invalid:
    edades_hijos = []

valid_edades_hijos = True
if cantidad_hijos > 0:
    if edades_hijos_invalid:
        st.sidebar.warning("Ingrese edades válidas separadas por coma, por ejemplo: 5, 8, 12.")
        valid_edades_hijos = False
    elif len(edades_hijos) != cantidad_hijos:
        st.sidebar.warning(
            f"La cantidad de edades ingresadas ({len(edades_hijos)}) no coincide con el número de hijos ({cantidad_hijos})."
        )
        valid_edades_hijos = False

st.sidebar.markdown("---")
st.sidebar.button("Limpiar formulario", on_click=reset_form)

register_click = st.sidebar.button("Registrar venta")

# -----------------------------------
# LÓGICA
# -----------------------------------

zona = zonas[estado]
califica, paquete, vigencia, motivo, beneficios, destinos_recomendados, cruceros_recomendados = compute_package(
    estado_civil,
    edad,
    residencia,
    cantidad_hijos,
    edades_hijos
)


deducible = st.session_state["deducible"]

ganancia = deducible * porcentaje

total = ganancia * ventas

if register_click:
    if not valid_edades_hijos:
        st.session_state["message"] = (
            "Corrija las edades de los hijos antes de registrar la venta. "
            "Asegúrese de que el número de edades coincida con la cantidad de hijos."
        )
    else:
        record = {
            "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "cliente": cliente,
            "estado": estado,
            "estado_civil": estado_civil,
            "edad": edad,
            "residencia": residencia,
            "zona": zona,
            "destino": "No aplica",
            "hotel": "No aplica",
            "paquete": paquete,
            "vigencia": vigencia,
            "deducible": deducible,
            "comision": porcentaje,
            "ventas": ventas,
            "ganancia_unitaria": ganancia,
            "total": total,
            "cantidad_hijos": cantidad_hijos,
            "edades_hijos": ", ".join(str(x) for x in edades_hijos),
            "beneficios": ", ".join(beneficios),
            "destinos_recomendados": ", ".join(destinos_recomendados),
            "cruceros_recomendados": ", ".join(cruceros_recomendados),
            "asesor": st.session_state["username"]
        }
        save_sale(record)
        st.session_state["message"] = "Venta registrada correctamente. Puede iniciar una nueva operación con Limpiar formulario."
        st.session_state["sale_registered"] = True

# -----------------------------------
# INTERFAZ
# -----------------------------------

st_title_str = "Deal"
st.title(st_title_str)
st.write("Sistema de calificación y registro de ventas para paquetes vacacionales.")

# --- Panel admin (solo visible para role == 'admin')
if st.session_state.get("role") == "admin":
    st.sidebar.markdown("## Panel Admin")
    admin_buttons = [
        "Dashboard",
        "Ventas",
        "Usuarios",
        "Clientes (Historial)",
        "Hoteles",
        "Paquetes",
        "Comisiones",
        "Estadísticas",
        "Seguimiento",
        "Configuración",
    ]

    # Inicializar sección admin en session_state
    if "admin_section" not in st.session_state:
        st.session_state["admin_section"] = "Dashboard"

    for name in admin_buttons:
        if st.sidebar.button(name):
            st.session_state["admin_section"] = name

    st.sidebar.markdown("---")

    admin_section = st.session_state.get("admin_section", "Dashboard")

    if admin_section == "Dashboard":
        st.subheader("Dashboard rápido")
        ventas = load_sales()
        total_ventas = len(ventas)
        total_ingresos = sum(float(v.get("total") or 0) for v in ventas)
        hoy = datetime.now().date().isoformat()
        ventas_hoy = sum(1 for v in ventas if v.get("timestamp", "")[:10] == hoy)

        # Mejor asesor del mes
        from collections import Counter
        now = datetime.now()
        ym = f"{now.year}-{now.month:02d}"
        ventas_mes = [v for v in ventas if v.get("timestamp", "")[:7] == ym]
        mejor_asesor = None
        if ventas_mes:
            asesores_mes = [v.get("asesor") for v in ventas_mes if v.get("asesor")]
            if asesores_mes:
                mejor_asesor = Counter(asesores_mes).most_common(1)[0][0]
        porcentaje_conversion = None
        if total_ventas > 0:
            porcentaje_conversion = f"{(len(ventas_mes)/total_ventas*100):.1f}%"

        st.metric("Total ventas", total_ventas)
        st.metric("Ingresos totales (USD)", f"${total_ingresos:,.2f}")
        st.metric("Ventas hoy", ventas_hoy)
        st.write(f"Mejor asesor del mes: {mejor_asesor or 'N/A'}")
        st.write(f"Porcentaje de ventas este mes vs totales: {porcentaje_conversion or 'N/A'}")

    if admin_section == "Usuarios":
        st.subheader("Gestión de usuarios")
        users_list = [{"username": k, **v} for k, v in USERS.items()]
        st.dataframe(users_list)

        st.markdown("**Crear asesor**")
        new_user = st.text_input("Usuario (username)", key="new_user")
        new_name = st.text_input("Nombre completo", key="new_name")
        new_pass = st.text_input("Contraseña", type="password", key="new_pass")
        if st.button("Crear asesor"):
            if not new_user or not new_pass:
                st.error("Usuario y contraseña obligatorios")
            else:
                USERS[new_user] = {"name": new_name or new_user, "role": "asesor", "password": new_pass}
                persist_users()
                st.success("Asesor creado")

        st.markdown("**Modificar / eliminar usuario**")
        sel_user = st.selectbox("Seleccionar usuario", sorted(list(USERS.keys())), key="sel_user")
        if sel_user:
            info = USERS.get(sel_user, {})
            st.write(info)
            if st.button("Borrar usuario"):
                if sel_user == st.session_state.get("username"):
                    st.error("No puede borrarse a sí mismo")
                else:
                    USERS.pop(sel_user, None)
                    persist_users()
                    st.success("Usuario eliminado")

            new_pw = st.text_input("Nueva contraseña", type="password", key="chg_pw")
            if st.button("Cambiar contraseña"):
                if new_pw:
                    USERS[sel_user]["password"] = new_pw
                    persist_users()
                    st.success("Contraseña actualizada")
                else:
                    st.error("Ingrese una contraseña válida")

            bloquear = st.checkbox("Bloquear cuenta", value=USERS.get(sel_user, {}).get("blocked", False), key="block")
            if st.button("Aplicar bloqueo"):
                USERS[sel_user]["blocked"] = bloquear
                persist_users()
                st.success("Estado de bloqueo actualizado")

    if admin_section == "Clientes (Historial)":
        st.subheader("Historial completo de clientes")
        ventas_guardadas = load_sales()
        st.dataframe(ventas_guardadas)

    if admin_section == "Hoteles":
        st.subheader("Hoteles y destinos")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Hoteles por ciudad")
            for ciudad, lista in hoteles.items():
                st.write(f"- {ciudad}: {', '.join(lista)}")
        with col2:
            ciudad = st.text_input("Ciudad a agregar")
            hotel = st.text_input("Hotel / Resort a agregar")
            if st.button("Agregar hotel"):
                if ciudad and hotel:
                    hoteles.setdefault(ciudad, [])
                    hoteles[ciudad].append(hotel)
                    persist_hoteles()
                    st.success("Hotel agregado")
                else:
                    st.error("Ciudad y hotel requeridos")

            ciudad_del = st.selectbox("Ciudad para eliminar hotel", sorted(list(hoteles.keys())), key="ciudad_del")
            hotel_del = st.selectbox("Hotel", hoteles.get(ciudad_del, []), key="hotel_del")
            if st.button("Eliminar hotel seleccionado"):
                if hotel_del in hoteles.get(ciudad_del, []):
                    hoteles[ciudad_del].remove(hotel_del)
                    persist_hoteles()
                    st.success("Hotel eliminado")

    if admin_section == "Paquetes":
        st.subheader("Editar paquetes")
        for key, meta in PACKAGES.items():
            st.markdown(f"**{key}**")
            v = st.text_input(f"Vigencia {key}", value=meta.get("vigencia", ""), key=f"vig_{key}")
            r = st.text_area(f"Requisitos {key}", value=meta.get("requisitos", ""), key=f"req_{key}")
            if st.button(f"Guardar {key}"):
                PACKAGES[key]["vigencia"] = v
                PACKAGES[key]["requisitos"] = r
                persist_packages()
                st.success(f"Paquete {key} actualizado")

        st.markdown("Agregar nuevo paquete")
        np_name = st.text_input("Nombre paquete nuevo", key="np_name")
        np_vig = st.text_input("Vigencia", key="np_vig")
        np_req = st.text_area("Requisitos", key="np_req")
        if st.button("Agregar paquete nuevo"):
            if np_name:
                PACKAGES[np_name] = {"vigencia": np_vig, "requisitos": np_req}
                persist_packages()
                st.success("Paquete agregado")
            else:
                st.error("Nombre requerido")

    if admin_section == "Estadísticas":
        st.subheader("Estadísticas detalladas")
        ventas = load_sales()
        total_ventas = len(ventas)
        total_ingresos = sum(float(v.get("total") or 0) for v in ventas)
        st.write(f"Total ventas: {total_ventas}")
        st.write(f"Ingresos totales: ${total_ingresos:,.2f}")
        # Conversión simple: ventas / registros (no hay leads separados)
        st.write("Conversión: no disponible (sin leads)")

    if admin_section == "Comisiones":
        st.subheader("Comisiones por asesor")
        ventas = load_sales()
        comps = {}
        for v in ventas:
            a = v.get("asesor") or "unknown"
            comps.setdefault(a, 0)
            try:
                comps[a] += float(v.get("total") or 0)
            except Exception:
                pass
        st.dataframe([{"asesor": k, "total_ingresos": v} for k, v in comps.items()])

    if admin_section == "Seguimiento":
        st.subheader("Seguimiento de clientes")
        st.write("Agregar seguimiento")
        f_cliente = st.text_input("Cliente", key="f_cliente")
        f_asesor = st.text_input("Asesor asignado", key="f_asesor")
        f_status = st.selectbox("Estado", ["interesado", "llamada pendiente", "venta cerrada", "no contestó"], key="f_status")
        f_note = st.text_area("Nota", key="f_note")
        if st.button("Agregar seguimiento"):
            FOLLOWUPS.append({
                "timestamp": datetime.now().isoformat(sep=" ", timespec="seconds"),
                "cliente": f_cliente,
                "asesor": f_asesor,
                "status": f_status,
                "nota": f_note,
            })
            persist_followups()
            st.success("Seguimiento agregado")

        if FOLLOWUPS:
            st.dataframe(FOLLOWUPS)

    if admin_section == "Configuración":
        st.subheader("Configuración de la empresa")
        porc = st.number_input("Porcentaje comisión por defecto", value=CONFIG.get("porcentaje_default", 0.06) * 100) / 100
        if st.button("Guardar configuración"):
            CONFIG["porcentaje_default"] = porc
            CONFIG["horarios"] = CONFIG.get("horarios", horarios)
            CONFIG["zonas"] = CONFIG.get("zonas", zonas)
            persist_config()
            st.success("Configuración guardada")

    st.markdown("---")

    # Logout al final de la barra lateral: estilo rojo para el último botón
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <style>
        [data-testid="stSidebar"] .stButton > button:last-child{background-color:#d9534f;color:white;border:0;padding:6px 12px;border-radius:4px}
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Cerrar sesión", key="cerrar_sesion"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["user_fullname"] = ""
        st.session_state["role"] = ""
        st.session_state["message"] = ""
        try:
            st.experimental_rerun()
        except Exception:
            st.stop()

show_records = st.checkbox(
    "Ver registros de ventas",
    value=st.session_state.get("show_records", False),
    key="show_records"
)

if show_records:
    ventas_guardadas = load_sales()
    if st.session_state["role"] == "asesor":
        ventas_guardadas = [v for v in ventas_guardadas if v.get("asesor") == st.session_state["username"]]

    if ventas_guardadas:
        st.subheader("Registros de ventas")
        st.dataframe(ventas_guardadas, use_container_width=True)
    else:
        st.info("No hay ventas registradas aún.")

# Mostrar bloque de ventas/resultado solo si no estamos en una sección admin distinta de 'Ventas'
show_sales = True
if st.session_state.get("role") == "admin":
    if st.session_state.get("admin_section") and st.session_state.get("admin_section") != "Ventas":
        show_sales = False

if show_sales:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Ventas")

        st.markdown(f"**Cliente:** {cliente or ''}")
        st.markdown(f"**Paquete ideal:** {paquete}")
        st.markdown(f"**Vigencia:** {vigencia}")
        st.markdown(f"**Deducible:** ${deducible}")

        st.markdown("---")
        st.markdown("**Zona y horario**")
        st.markdown(f"Zona detectada: {zona}")
        st.markdown(f"Horario: {horarios.get(zona, 'N/A')}")

        st.markdown("---")
        st.markdown("**Destinos y hoteles disponibles**")
        for ciudad, lista_hoteles in hoteles.items():
            st.markdown(f"- {ciudad}")
            for hotel_item in lista_hoteles:
                st.write(f"  - {hotel_item}")

        st.markdown("---")
        st.subheader("Speech")
        if califica:
            st.write(
                "El cliente califica para un paquete especial. Puede comunicarle que el viaje ya está aprobado y que solo necesita cubrir el deducible para comenzar a reservar. Recuérdale que este paquete ofrece una vigencia amplia y un plan diseñado para maximizar su experiencia de vacaciones con el menor esfuerzo posible."
            )
        else:
            st.write(
                "El cliente no cumple los requisitos para los paquetes preferenciales en este momento. Ofrece la alternativa MIX & MATCH, destacando los beneficios del plan y la posibilidad de mantener el interés mientras se busca una opción adecuada."
            )

    with col2:
        st.subheader("Comisión")
        st.markdown(f"**Total:** ${total:,.2f} USD")
        st.markdown(f"**Ganancia por unidad:** ${ganancia:,.2f}")

        st.markdown("---")
        if st.session_state["message"]:
            st.success(st.session_state["message"])

st.markdown(
"""
### Acerca de la aplicación
Esta herramienta ayuda a los asesores a evaluar clientes y registrar cada venta con la información clave: nombre, estado, edad, residencia, destino, hotel, paquete y comisiones.
"""
)
