# =============================================================
# MODELO MACHINE LEARNING - 4 ALGORITMOS
# Plataforma BI - Congestión Vehicular Lima Norte
# =============================================================

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score
from sklearn.preprocessing import LabelEncoder
import json, sys, os, glob

# =============================================================
# DETECCIÓN AUTOMÁTICA DEL CSV (Opción 3 - valida columnas)
# =============================================================

COLUMNAS_REQUERIDAS = [
    'fecha', 'hora', 'distrito', 'avenida_via',
    'condicion_clima', 'tipo_evento', 'vehiculo_predominante',
    'velocidad_promedio', 'flujo_vehicular',
    'congestion_score', 'tiempo_viaje'
]

carpeta_ml = os.path.dirname(os.path.abspath(__file__))
carpeta    = os.path.dirname(carpeta_ml)  # carpeta raíz del proyecto

# Busca todos los CSV en la raíz
archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))

if not archivos_csv:
    print("ERROR: No se encontró ningún archivo CSV en la carpeta raíz.")
    sys.exit(1)

csv_valido = None
for archivo in archivos_csv:
    try:
        df_test = pd.read_csv(archivo, nrows=1)
        columnas_presentes = [col for col in COLUMNAS_REQUERIDAS if col in df_test.columns]
        if len(columnas_presentes) == len(COLUMNAS_REQUERIDAS):
            csv_valido = archivo
            print(f"[OK] CSV válido encontrado: {os.path.basename(archivo)}")
            break
        else:
            faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df_test.columns]
            print(f"[SKIP] {os.path.basename(archivo)} — faltan columnas: {faltantes}")
    except Exception as e:
        print(f"[SKIP] {os.path.basename(archivo)} — error al leer: {e}")
        continue

if not csv_valido:
    print("ERROR: Ningún CSV tiene las columnas requeridas para el modelo.")
    print(f"Columnas necesarias: {COLUMNAS_REQUERIDAS}")
    sys.exit(1)

df = pd.read_csv(csv_valido)
print(f"[OK] {len(df)} registros cargados.")

# =============================================================
# FEATURE ENGINEERING
# =============================================================

df['fecha']      = pd.to_datetime(df['fecha'])
df['dia_semana'] = df['fecha'].dt.dayofweek
df['mes']        = df['fecha'].dt.month

le = LabelEncoder()
df['clima_enc']    = le.fit_transform(df['condicion_clima'])
df['evento_enc']   = le.fit_transform(df['tipo_evento'])
df['via_enc']      = le.fit_transform(df['avenida_via'])
df['distrito_enc'] = le.fit_transform(df['distrito'])
df['vehiculo_enc'] = le.fit_transform(df['vehiculo_predominante'])

# Etiquetas para clasificación
def nivel_congestion(score):
    if score < 40:   return 'Bajo'
    elif score < 70: return 'Medio'
    else:            return 'Alto'

def zona_critica(score):
    return 'Crítica' if score >= 70 else 'No Crítica'

df['nivel_congestion'] = df['congestion_score'].apply(nivel_congestion)
df['zona_critica']     = df['congestion_score'].apply(zona_critica)

# Features comunes
FEATURES = [
    'hora', 'dia_semana', 'mes',
    'clima_enc', 'evento_enc', 'via_enc',
    'distrito_enc', 'vehiculo_enc',
    'velocidad_promedio', 'flujo_vehicular'
]

X = df[FEATURES]

# =============================================================
# MODELO 1: Regresión Lineal → Tiempo de Viaje
# =============================================================

y1 = df['tiempo_viaje']
X1_train, X1_test, y1_train, y1_test = train_test_split(X, y1, test_size=0.2, random_state=42)

modelo1 = LinearRegression()
modelo1.fit(X1_train, y1_train)
y1_pred = modelo1.predict(X1_test)

r2_m1  = round(r2_score(y1_test, y1_pred) * 100, 2)
mse_m1 = round(mean_squared_error(y1_test, y1_pred), 2)
ejemplo_m1 = round(modelo1.predict([X1_test.iloc[0]])[0], 1)

print(f"[M1] Regresión Lineal (Tiempo Viaje) — R²: {r2_m1}% | MSE: {mse_m1}")

# =============================================================
# MODELO 2: Regresión Lineal → Flujo Vehicular
# =============================================================

y2 = df['flujo_vehicular']
X2_train, X2_test, y2_train, y2_test = train_test_split(X, y2, test_size=0.2, random_state=42)

modelo2 = LinearRegression()
modelo2.fit(X2_train, y2_train)
y2_pred = modelo2.predict(X2_test)

r2_m2  = round(r2_score(y2_test, y2_pred) * 100, 2)
mse_m2 = round(mean_squared_error(y2_test, y2_pred), 2)
ejemplo_m2 = round(modelo2.predict([X2_test.iloc[0]])[0], 0)

print(f"[M2] Regresión Lineal (Flujo Vehicular) — R²: {r2_m2}% | MSE: {mse_m2}")

# =============================================================
# MODELO 3: Árbol de Decisiones → Nivel de Congestión
# =============================================================

y3 = df['nivel_congestion']
X3_train, X3_test, y3_train, y3_test = train_test_split(X, y3, test_size=0.2, random_state=42)

modelo3 = DecisionTreeClassifier(max_depth=5, random_state=42)
modelo3.fit(X3_train, y3_train)
y3_pred = modelo3.predict(X3_test)

acc_m3    = round(accuracy_score(y3_test, y3_pred) * 100, 2)
ejemplo_m3 = modelo3.predict([X3_test.iloc[0]])[0]

print(f"[M3] Árbol Decisiones (Nivel Congestión) — Accuracy: {acc_m3}%")

# =============================================================
# MODELO 4: Árbol de Decisiones → Zona Crítica
# =============================================================

y4 = df['zona_critica']
X4_train, X4_test, y4_train, y4_test = train_test_split(X, y4, test_size=0.2, random_state=42)

modelo4 = DecisionTreeClassifier(max_depth=5, random_state=42)
modelo4.fit(X4_train, y4_train)
y4_pred = modelo4.predict(X4_test)

acc_m4    = round(accuracy_score(y4_test, y4_pred) * 100, 2)
ejemplo_m4 = modelo4.predict([X4_test.iloc[0]])[0]

print(f"[M4] Árbol Decisiones (Zona Crítica) — Accuracy: {acc_m4}%")

# =============================================================
# ZONAS CRÍTICAS POR DISTRITO
# =============================================================

zonas_criticas = (
    df[df['zona_critica'] == 'Crítica']
    .groupby('distrito')
    .size()
    .reset_index(name='casos')
    .sort_values('casos', ascending=False)
    .head(5)
)

zonas_lista = [
    {
        "zona": row['distrito'],
        "probabilidad": round(row['casos'] / len(df) * 100, 1)
    }
    for _, row in zonas_criticas.iterrows()
]

# =============================================================
# EXPORTAR JSON
# =============================================================

resultado = {
    "archivo_procesado": os.path.basename(csv_valido),
    "total_registros": len(df),
    "metricas_principales": {
        "r2":       max(r2_m1, r2_m2),
        "accuracy": max(acc_m3, acc_m4),
        "mse":      mse_m1
    },
    "modelos": {
        "regresion_tiempo_viaje": {
            "r2":           r2_m1,
            "mse":          mse_m1,
            "ejemplo_salida": f"{ejemplo_m1} minutos"
        },
        "regresion_flujo_vehicular": {
            "r2":           r2_m2,
            "mse":          mse_m2,
            "ejemplo_salida": f"{int(ejemplo_m2)} vehículos"
        },
        "arbol_nivel_congestion": {
            "accuracy":     acc_m3,
            "ejemplo_salida": ejemplo_m3
        },
        "arbol_zona_critica": {
            "accuracy":     acc_m4,
            "ejemplo_salida": ejemplo_m4
        }
    },
    "zonas_criticas": zonas_lista
}

output_path = os.path.join(carpeta_ml, 'predicciones_ml.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"\n[OK] predicciones_ml.json generado correctamente.")
print(f"[OK] Archivo procesado: {os.path.basename(csv_valido)}")
print(f"[OK] Registros analizados: {len(df)}")