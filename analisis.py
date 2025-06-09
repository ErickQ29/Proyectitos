import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuración del acceso al dataset ---
# Elige una de las siguientes opciones:

# Opción 1: Dataset local (recomendado para empezar)
# Asegúrate de que 'process_data_multi_snapshot_raw.csv' esté en el mismo directorio que este script,
# o especifica la ruta completa del archivo.
dataset_path = "process_data_multi_snapshot_raw.csv"

# Opción 2: Dataset en un enlace público (descomentar y reemplazar si aplica)
# Si has subido tu dataset a GitHub, Google Drive, etc., obtén el enlace directo al archivo RAW.
# dataset_url = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/process_data_multi_snapshot_raw.csv"


# --- Cargar el dataset ---
try:
    # Intenta cargar desde la ruta local primero
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        print(f"Dataset cargado exitosamente desde: {os.path.abspath(dataset_path)}")
    # Si no, intenta cargar desde una URL (si está definida y descomentada)
    # elif 'dataset_url' in locals() and dataset_url:
    #     df = pd.read_csv(dataset_url)
    #     print(f"Dataset cargado exitosamente desde la URL: {dataset_url}")
    else:
        raise FileNotFoundError(f"El archivo '{dataset_path}' no se encontró localmente.")

except FileNotFoundError as e:
    print(f"Error al cargar el dataset: {e}")
    print("Asegúrate de que 'process_data_multi_snapshot_raw.csv' esté en el mismo directorio")
    print("o que la 'dataset_url' esté correctamente configurada y accesible.")
    exit() # Salir si el archivo no se puede cargar

print("\n--- Vista previa del Dataset ---")
print(df.head())

print("\n--- Información General del Dataset ---")
df.info()

# --- Preprocesamiento: Asegurar que las columnas numéricas sean de tipo numérico ---
# Define las columnas que deben ser numéricas para el análisis estadístico y de correlación.
# Estas columnas incluyen las nuevas métricas añadidas en la recopilación de datos más profunda.
numeric_cols = ['cpu_percent', 'memory_mb', 'num_threads',
                'num_connections', 'num_open_files', 'io_read_bytes',
                'io_write_bytes', 'memory_percent']

# Filtrar solo las columnas que realmente existen en el DataFrame
existing_numeric_cols = [col for col in numeric_cols if col in df.columns]

# Convertir las columnas identificadas a tipo numérico.
# 'coerce' convertirá cualquier valor no numérico (como los -1 de acceso denegado) a NaN (Not a Number).
for col in existing_numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Eliminar filas que contengan valores NaN en las columnas numéricas que usaremos.
# Esto es crucial para asegurar que los cálculos estadísticos no fallen y sean precisos.
df.dropna(subset=existing_numeric_cols, inplace=True)
print(f"\nDataset después de limpiar valores NaN en columnas numéricas. Filas restantes: {len(df)}")


# --- Estadísticas Básicas ---
print("\n--- Estadísticas Básicas de las Variables Numéricas ---")
print("\nMedia (Promedio):")
print(df[existing_numeric_cols].mean())

print("\nMediana (Valor central):")
print(df[existing_numeric_cols].median())

print("\nModa (Valor(es) más frecuente(s)):")
for col in existing_numeric_cols:
    if not df[col].mode().empty:
        # La moda puede devolver múltiples valores si tienen la misma frecuencia,
        # .tolist() los convierte en una lista para una mejor visualización.
        print(f"{col}: {df[col].mode().tolist()}")
    else:
        print(f"{col}: No hay una moda única o valores.")

print("\nDesviación Estándar (Medida de la dispersión de los datos):")
print(df[existing_numeric_cols].std())


# --- Matriz de Correlación entre Variables Numéricas ---
print("\n--- Matriz de Correlación entre Variables Numéricas ---")
# La correlación mide la fuerza y dirección de una relación lineal entre dos variables.
# Los valores van de -1 (correlación negativa perfecta) a 1 (correlación positiva perfecta).
# 0 indica que no hay relación lineal.
correlation_matrix = df[existing_numeric_cols].corr()
print(correlation_matrix)

# --- Visualización de la Matriz de Correlación (Opcional, requiere matplotlib y seaborn) ---
# Esta parte crea un mapa de calor para visualizar la matriz de correlación,
# lo que facilita la identificación de relaciones y patrones.
print("\nGenerando mapa de calor de la matriz de correlación...")
try:
    plt.figure(figsize=(10, 8)) # Ajustar el tamaño de la figura para acomodar más columnas
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, linecolor='black')
    plt.title('Matriz de Correlación de Procesos del Sistema')
    plt.show()
    print("Mapa de calor de la matriz de correlación generado. Cierre la ventana emergente para continuar.")
except Exception as e:
    print(f"No se pudo generar el mapa de calor. Asegúrate de tener 'matplotlib' y 'seaborn' instalados.")
    print(f"Error detallado: {e}")

# --- Conteo de Procesos Legítimos vs. Maliciosos ---
# Esto solo tendrá sentido si has clasificado manualmente la columna 'is_malicious'
# después de generar el CSV con el script de recopilación.
print("\n--- Conteo de Procesos por Clasificación ('is_malicious') ---")
if 'is_malicious' in df.columns:
    print(df['is_malicious'].value_counts())
else:
    print("La columna 'is_malicious' no se encontró en el dataset para el conteo.")

print("\nAnálisis del dataset completado.")
