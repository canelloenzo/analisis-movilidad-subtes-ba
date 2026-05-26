import pandas as pd
from sqlalchemy import create_engine, text
import pymysql # Asegúrate de que esté instalado

print("1. Cargando los archivos CSV en memoria...")
# Cargo los dataframes (Asegúrate de que las rutas sean correctas)
df_estaciones = pd.read_csv('data/BaseUnificadaEstaciones.csv', sep=',')
df_molinetes = pd.read_csv('data/historico_2021.csv', sep=';')

# Limpio espacios invisibles en los nombres de las columnas para evitar errores de acceso
df_molinetes.columns = df_molinetes.columns.str.strip()

print("1.5. Limpiando y Transformando los datos...")

print(" -> Fase 1: Manejo de nulos...")
# 1. Identificación y manejo de valores faltantes/nulos
# Elimino filas con nulos críticos en la tabla de hechos (molinetes), ya que no me sirve un registro de viaje incompleto
df_molinetes.dropna(inplace=True)
# Para las estaciones (tabla dimensional), relleno los nulos con 'Sin Datos' para no perder dimensiones
df_estaciones.fillna('Sin Datos', inplace=True)

print(" -> Fase 2: Transformación de fechas...")
print("Columnas disponibles en molinetes:", df_molinetes.columns.tolist())
# 2. Transformación de variables y formato de fechas
# Convierto la columna que almacena la fecha (asumo que se llama 'fecha') a formato datetime. 
# Fuerzo los errores a 'coerce' para que los textos inválidos pasen a NaT (Not a Time)
df_molinetes['FECHA'] = pd.to_datetime(df_molinetes['FECHA'], dayfirst=True, errors='coerce')

# Filtro y elimino los registros que hayan quedado como NaT tras la conversión
df_molinetes.dropna(subset=['FECHA'], inplace=True)
print(f"Filas disponibles tras limpiar fechas: {len(df_molinetes)}")

# Extraigo y creo variables derivadas basadas en la fecha para facilitar futuras agrupaciones
df_molinetes['dia_semana'] = df_molinetes['FECHA'].dt.day_name()
df_molinetes['mes'] = df_molinetes['FECHA'].dt.month
# Extraigo la hora del viaje para analizar posteriormente las horas pico
df_molinetes['hora'] = df_molinetes['FECHA'].dt.hour

print(" -> Fase 3: Detección de outliers...")
# Convierto la columna 'TOTAL' a formato numérico puro para evitar errores de tipo al calcular estadísticas.
# Antes, remuevo cualquier separador de miles u otros caracteres extraños usando expresiones regulares.
if 'pax_TOTAL' in df_molinetes.columns and df_molinetes['pax_TOTAL'].dtype == object:
    df_molinetes['pax_TOTAL'] = df_molinetes['pax_TOTAL'].astype(str).str.replace(r'[^0-9]', '', regex=True)

df_molinetes['pax_TOTAL'] = pd.to_numeric(df_molinetes['pax_TOTAL'], errors='coerce')
df_molinetes.dropna(subset=['pax_TOTAL'], inplace=True)
print(f"Filas disponibles para calcular outliers: {len(df_molinetes)}")

# 3. Detección y tratamiento de outliers (usando rangos intercuartílicos - IQR)
# Calculo los cuartiles Q1 y Q3 para la variable de pasajeros
Q1 = df_molinetes['pax_TOTAL'].quantile(0.25)
Q3 = df_molinetes['pax_TOTAL'].quantile(0.75)
IQR = Q3 - Q1

# Defino los límites y filtro los registros para eliminar los valores atípicos
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR
df_molinetes = df_molinetes[(df_molinetes['pax_TOTAL'] >= limite_inferior) & (df_molinetes['pax_TOTAL'] <= limite_superior)]

print(" -> Fase 4: Normalización...")
# 4. Normalización y escalado de variables numéricas
# Aplico escalado Min-Max para normalizar la variable y dejarla en un rango de 0 a 1
min_pax = df_molinetes['pax_TOTAL'].min()
max_pax = df_molinetes['pax_TOTAL'].max()
df_molinetes['pax_TOTAL_norm'] = (df_molinetes['pax_TOTAL'] - min_pax) / (max_pax - min_pax)

# Configuro las credenciales (asumiendo entorno local estándar sin contraseña)
usuario = 'root'
contrasena = '' # <- Dejado en blanco para conexiones locales por defecto
host = 'localhost'
puerto = '3306'

print("2. Conectando al servidor MySQL...")
# Creo una conexión inicial para generar la base de datos si no existe
engine_server = create_engine(f"mysql+pymysql://{usuario}:{contrasena}@{host}:{puerto}")
with engine_server.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS subtes_ba;"))
    print("Base de datos 'subtes_ba' creada.")

print("3. Exportando datos a las tablas relacionales...")
# Creo el motor apuntando a la nueva base de datos
base_datos = 'subtes_ba'
string_conexion = f"mysql+pymysql://{usuario}:{contrasena}@{host}:{puerto}/{base_datos}"
engine = create_engine(string_conexion)

# Fase de Carga (Load)
df_estaciones.to_sql(name='dim_estaciones', con=engine, if_exists='replace', index=False)
print("Tabla dimensional 'dim_estaciones' cargada con éxito.")

print("Cargando la tabla de hechos (esto puede demorar unos minutos, son +7 millones de registros)...")
df_molinetes.to_sql(name='fact_viajes_2021', con=engine, if_exists='replace', index=False, chunksize=100000)
print("Tabla de hechos 'fact_viajes_2021' cargada con éxito.")

print("Exportando datasets transformados a CSV para Power BI...")
df_estaciones.to_csv('data/dim_estaciones_limpio.csv', index=False, sep=',')
df_molinetes.to_csv('data/fact_viajes_2021_limpio.csv', index=False, sep=',')
print("¡Archivos en csv listos para visualizar!")