import psutil
import pandas as pd
import datetime
import os
import time # Se ha añadido para usar time.sleep()

# Función para obtener información de los procesos activos
def get_process_info(snapshot_time_str):
    """
    Recopila información detallada de todos los procesos activos en el sistema
    en un momento específico (snapshot_time_str).
    Incluye más atributos como conexiones de red, archivos abiertos y contadores de E/S.
    """
    processes_data = []
    # Iterar sobre todos los procesos para obtener sus objetos Process
    for proc in psutil.process_iter():
        try:
            # Obtener atributos básicos del proceso
            pinfo = proc.as_dict(attrs=['pid', 'name', 'exe', 'username', 'cpu_percent', 'memory_info', 'num_threads', 'status', 'create_time', 'cmdline'])

            # Añadir el timestamp de la captura actual
            pinfo['snapshot_time'] = snapshot_time_str

            # Procesar el uso de memoria para convertirlo a MB
            pinfo['memory_mb'] = pinfo['memory_info'].rss / (1024 * 1024) if pinfo['memory_info'] else 0
            del pinfo['memory_info'] # Eliminar el objeto original de memory_info para mantener el CSV limpio

            # Convertir el tiempo de creación (timestamp) a un formato legible
            pinfo['create_time_readable'] = datetime.datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            del pinfo['create_time'] # Eliminar el timestamp original

            # Unir los argumentos de línea de comandos en un solo string
            pinfo['cmdline_str'] = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
            del pinfo['cmdline'] # Eliminar la lista original de cmdline

            # --- Información más profunda y especializada ---

            # Número de conexiones de red abiertas por el proceso
            try:
                pinfo['num_connections'] = len(proc.connections(kind='inet'))
            except psutil.AccessDenied:
                pinfo['num_connections'] = -1 # -1 para indicar acceso denegado

            # Número de archivos abiertos por el proceso
            try:
                pinfo['num_open_files'] = len(proc.open_files())
            except psutil.AccessDenied:
                pinfo['num_open_files'] = -1 # -1 para indicar acceso denegado

            # Contadores de E/S (Input/Output)
            try:
                io_counters = proc.io_counters()
                pinfo['io_read_bytes'] = io_counters.read_bytes
                pinfo['io_write_bytes'] = io_counters.write_bytes
            except psutil.AccessDenied:
                pinfo['io_read_bytes'] = -1
                pinfo['io_write_bytes'] = -1

            # Porcentaje de memoria RAM utilizada por el proceso (del total del sistema)
            try:
                pinfo['memory_percent'] = proc.memory_percent()
            except psutil.AccessDenied:
                pinfo['memory_percent'] = -1

            # Añadir una columna inicial para la clasificación de 'malicioso' o 'legítimo'
            pinfo['is_malicious'] = 'unknown'

            processes_data.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignorar procesos que ya no existen, a los que no se tiene acceso, o que son "zombies"
            pass
    return processes_data

if __name__ == "__main__":
    all_snapshots_data = [] # Lista para almacenar los datos de todas las capturas
    num_snapshots = 4 # Número total de capturas a tomar
    interval_seconds = 15 # Intervalo entre cada captura en segundos
    total_duration_minutes = (num_snapshots * interval_seconds) / 60 # Duración total en minutos

    print(f"Iniciando la recopilación de información de procesos activos en {num_snapshots} capturas.")
    print(f"Cada captura se tomará cada {interval_seconds} segundos, por un total de {total_duration_minutes:.0f} minuto(s).")

    for i in range(num_snapshots):
        current_time = datetime.datetime.now()
        snapshot_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nTomando captura {i+1}/{num_snapshots} a las {snapshot_time_str}...")

        snapshot_data = get_process_info(snapshot_time_str)
        all_snapshots_data.extend(snapshot_data) # Añadir los datos de la captura actual a la lista global

        # Esperar el intervalo de tiempo antes de la siguiente captura, excepto después de la última
        if i < num_snapshots - 1:
            print(f"Esperando {interval_seconds} segundos para la próxima captura...")
            time.sleep(interval_seconds)

    # Crear un DataFrame de pandas con todos los datos recopilados de todas las capturas
    df = pd.DataFrame(all_snapshots_data)

    # Definir el nombre del archivo de salida para el dataset multi-captura
    output_filename = "process_data_multi_snapshot_raw.csv"

    # Guardar el DataFrame en un archivo CSV
    df.to_csv(output_filename, index=False, encoding='utf-8')
    print(f"\nDataset completo de procesos guardado exitosamente en '{os.path.abspath(output_filename)}'")
    print("Muestra de las primeras 5 filas del dataset combinado:")
    print(df.head())

    print("\n¡Importante! Ahora, por favor, abre el archivo 'process_data_multi_snapshot_raw.csv'")
    print("y revisa la columna 'is_malicious'. Cambia 'unknown' a 'legitimate' o 'malicious'")
    print("para algunos procesos según tu criterio. Luego, guarda el archivo como 'process_data_multi_snapshot_classified.csv'.")
    print("¡No subas datos sensibles sin anonimizar!")
