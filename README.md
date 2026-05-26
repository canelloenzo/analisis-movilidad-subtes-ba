# Análisis de Movilidad Urbana: Red de Subtes (2021)

**Autor:** Enzo German Canello  
**Herramientas Utilizadas:** Python, Power BI, DAX  

---

## 1. Resumen Ejecutivo
El presente proyecto consiste en el desarrollo de una solución integral de Business Intelligence orientada a analizar el tráfico de pasajeros de la red de subterráneos de Buenos Aires durante el año 2021. El objetivo principal fue transformar un volumen masivo de datos transaccionales brutos en información estratégica, facilitando la identificación de patrones de demanda, comportamiento del usuario y cuellos de botella operativos para la toma de decisiones basada en evidencia.

Se identificó que la red procesó 61 millones de viajes en el periodo, con una fuerte concentración operativa en las Líneas B y D (casi el 50% del volumen total). Además, el análisis financiero demostró una alta rentabilidad base por venta directa, con un 93,82% de pasajeros abonando la tarifa completa. A nivel operativo, se detectó una demanda de perfil *commuter*, con una franja crítica de saturación que se extiende desde las 13:00 hasta pasadas las 17:00 horas.

## 2. Extracción, Transformación y Carga (Proceso ETL)

### 2.1 Limpieza y Exploración de Datos
La fase inicial se desarrolló mediante scripts en Python para la limpieza del dataset original. Durante esta auditoría exploratoria, se identificó un vacío de registros operativos correspondiente a los meses de febrero y marzo. Este hallazgo fue documentado para evitar sesgos en las proyecciones anuales, garantizando que el análisis posterior refleje únicamente los datos reales capturados.

### 2.2 Arquitectura 
Durante la etapa de integración, se presentó una limitación de conectividad al intentar establecer una conexión directa entre el entorno local de MySQL y Power BI Desktop. Para asegurar la integridad del pipeline y el cumplimiento del cronograma, se implementó una solución de contingencia técnica:
* Se añadieron comandos de exportación al flujo de procesamiento en Python para generar archivos `.csv` optimizados (`fact_viajes_2021_limpio.csv` y `dim_estaciones_limpio.csv`).
* Esta arquitectura desacoplada garantizó la limpieza de los datos y permitió que el modelo en Power BI se alimentara de fuentes estables, optimizando el rendimiento de las visualizaciones.

## 3. Modelado de Datos en Power BI
Para habilitar el análisis temporal y operativo, se optimizó el modelo de datos dentro de Power BI mediante la creación de columnas calculadas (DAX), evitando saturar el modelo con relaciones innecesarias de "varios a varios":
* **Ordenamiento Semanal:** Se creó la columna `NumeroDia` (`WEEKDAY`) para forzar el orden cronológico del gráfico de barras de Lunes a Domingo, superando el orden alfabético predeterminado.
* **Segmentación Horaria:** Ante la presencia de valores nulos o en formato incorrecto en la columna temporal original, se generó la columna `Hora_Real` utilizando la función `HOUR()` sobre el registro de la transacción (`DESDE`). Esto permitió desplegar correctamente la matriz de 24 horas.
* **Tipado de Datos:** Se ajustó la metadata de la columna `mes` a formato de "Número entero" para garantizar la correcta representación de la evolución cronológica en el eje X de las series temporales.

## 4. Visualización y Storytelling
El tablero se estructuró en dos páginas con una estética minimalista, priorizando el espacio negativo, la eliminación de ejes redundantes y una paleta de colores intencional para reducir la carga cognitiva.

### 4.1 Página 1: Visión Estratégica y Financiera
Diseñada para un perfil directivo, esta página responde a las métricas globales del negocio:
* **Volumen Total (Tarjeta KPI):** Fija la escala del negocio en 61 millones de pasajeros.
* **Tráfico por Línea (Barras Horizontales):** Identifica a las Líneas B (15,3 M) y D (14,3 M) como las arterias principales de la red.
* **Composición de Tarifa (Anillo):** Destruye el sesgo de dependencia de subsidios, demostrando que el 93,82% de los viajes se realizan bajo tarifa completa, frente a un volumen marginal (6,11%) de franquicias.
* **Estacionalidad Semanal y Mensual:** El tráfico por día evidencia una demanda rígida de lunes a viernes (10,5 M en promedio) con una caída drástica el fin de semana. La curva de evolución mensual muestra la tendencia de recuperación paulatina del sistema hacia diciembre (9,5 M).

### 4.2 Página 2: Análisis Operativo y Cuellos de Botella
Enfocada en equipos de logística y operaciones, esta vista cruza variables temporales y categóricas para detectar estrés en el sistema:
* **Curva Horaria (Gráfico de Áreas):** Expone la anatomía del día operativo. Muestra un primer salto de demanda en el ingreso laboral a las 8:00 a.m. Lejos de caer al mediodía, el tráfico se consolida en una meseta alta y continúa subiendo gradualmente hasta formar un bloque crítico durante toda la tarde.
* **Mapa de Calor (Matriz con Formato Condicional):** Se desarrolló utilizando un degradado de color (estilo Python/Seaborn) cruzando las líneas (filas) con la variable `Hora_Real` (columnas). Este gráfico es el *insight* definitivo del proyecto: demuestra que la saturación no es generalizada, sino que el colapso ocurre específicamente en las Líneas B y D, y que su franja de máxima tensión comienza a las 13:00 horas, manteniéndose en estado crítico continuo hasta pasadas las 17:00 horas.

## 5. Conclusiones y Valor Aportado
El desarrollo de este tablero permite a la organización transicionar de una gestión reactiva a una planificación proactiva basada en datos.
* **Priorización de Inversión:** Cualquier presupuesto destinado a mantenimiento de infraestructura o mejora de estaciones debe enfocarse prioritariamente en las Líneas B y D.
* **Solidez Financiera:** El modelo de negocio cuenta con un flujo de ingresos directo altamente predecible, dado que la composición tarifaria (94% pago completo) se mantiene estable independientemente de la época del año.
* **Gestión de Recursos Humanos y Logística:** La evidencia del Mapa de Calor indica que la inyección de formaciones de refuerzo y la flexibilización de turnos del personal no deben limitarse únicamente al horario de salida de oficinas (17:00 - 18:00), ya que el estado crítico de la red comienza a gestarse desde las 13:00 horas.

## 6. Anexo: Diccionario de Datos
A continuación, se detallan las métricas y campos clave utilizados para el desarrollo del modelo relacional y las visualizaciones del proyecto:
* **`pax_TOTAL`**: Volumen total de pasajeros procesados. Representa la métrica principal de demanda y volumen operativo de la red.
* **`pax_pagos`**: Cantidad de pasajeros que abonan la tarifa completa del servicio.
* **`pax_franq`**: Cantidad de pasajeros que viajan mediante franquicias o pases especiales (como jubilados, estudiantes, personal, entre otros).
* **`LINEA`**: Identificador categórico del ramal de la red de subterráneos al que pertenece la estación (A, B, C, D, E, H).
* **`mes`**: Periodo temporal de la transacción, extraído y expresado en formato numérico (del 1 al 12) para facilitar el ordenamiento cronológico.
* **`dia_semana`**: Clasificación en formato de texto del día correspondiente a la operación (Lunes a Domingo).
* **`DESDE`**: Marca de tiempo (Timestamp) original del registro en el molinete, que indica el momento exacto del viaje.
* **`Hora_Real`**: Campo calculado mediante funciones DAX que extrae únicamente la hora entera del campo "DESDE", utilizado específicamente para la segmentación del eje temporal en el mapa de calor y el gráfico de áreas.
