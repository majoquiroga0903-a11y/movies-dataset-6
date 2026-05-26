import csv
import os
from datetime import datetime

import streamlit as st

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
if st.sidebar.button("Cerrar sesión"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["user_fullname"] = ""
    st.session_state["role"] = ""
    st.session_state["message"] = ""
    st.stop()

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

st.title("Cerrador Pro")
st.write("Sistema de calificación y registro de ventas para paquetes vacacionales.")

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

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Resultado")

    if califica:
        st.success(
            f"Cliente: {cliente or 'No ingresado'}\n\n"
            f"Califica para: {paquete}\n\n"
            f"Vigencia: {vigencia}"
        )
    else:
        st.error(
            f"Cliente: {cliente or 'No ingresado'}\n\n"
            f"Enviar a MIX & MATCH\n\n"
            f"{motivo}"
        )

    if beneficios:
        st.subheader("Beneficios sugeridos")
        for beneficio in beneficios:
            st.write(f"• {beneficio}")

    if destinos_recomendados:
        st.subheader("Destinos recomendados")
        st.write(", ".join(destinos_recomendados))

    if cruceros_recomendados:
        st.subheader("Cruceros recomendados")
        st.write(", ".join(cruceros_recomendados))

    st.subheader("Hoteles por ciudad")
    for ciudad, lista_hoteles in hoteles.items():
        st.markdown(f"**{ciudad}**")
        for hotel_item in lista_hoteles:
            st.write(f"- {hotel_item}")

with col2:
    st.subheader("Zona y horario")
    st.info(f"Zona detectada: {zona}\nHorario: {horarios[zona]}")

    st.subheader("Comisión")
    st.write(f"Total: ${total:,.2f} USD")
    st.write(f"Ganancia por unidad: ${ganancia:,.2f}")

    st.subheader("Speech")
    if califica:
        st.success(
            "El cliente califica para un paquete especial. Puede comunicarle que el viaje ya está aprobado y que solo necesita cubrir el deducible para comenzar a reservar. Recuérdale que este paquete ofrece una vigencia amplia y un plan diseñado para maximizar su experiencia de vacaciones con el menor esfuerzo posible."
        )
    else:
        st.warning(
            "El cliente no cumple los requisitos para los paquetes preferenciales en este momento. Ofrece la alternativa MIX & MATCH, destacando los beneficios del plan y la posibilidad de mantener el interés mientras se busca una opción adecuada."
        )

    if st.session_state["message"]:
        st.success(st.session_state["message"])

st.markdown(
"""
### Acerca de la aplicación
Esta herramienta ayuda a los asesores a evaluar clientes y registrar cada venta con la información clave: nombre, estado, edad, residencia, destino, hotel, paquete y comisiones.
"""
)
