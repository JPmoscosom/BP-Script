import git
from collections import defaultdict
from pathlib import Path
import re
import mimetypes

# Ruta del repositorio Git local
repo_path = 'youtube-dl'

# Crear objeto repo
repo = git.Repo(repo_path)

# Obtener cantidad total de commits
total_commits = len(list(repo.iter_commits()))
print(f"Total de commits: {total_commits}")

# Obtener autores y sus contribuciones
autores = {}
for commit in repo.iter_commits():
    autor = commit.author.name
    if autor in autores:
        autores[autor] += 1
    else:
        autores[autor] = 1

print("\nContribuciones por autor:")
for autor, contribuciones in autores.items():
    print(f"{autor}: {contribuciones} commits")


def contar_lineas_codigo(ruta_repo):
    # Inicializar contadores
    contador_lineas = 0
    contador_archivos = 0

    # Recorrer cada archivo en el repositorio
    for archivo in repo.iter_trees():
        for blob in archivo.blobs:
            # Leer el contenido del archivo
            tipo_archivo = mimetypes.guess_type(blob.name)[0]

            if not tipo_archivo or tipo_archivo.startswith("application/"):
                continue

            try:
                contenido_archivo = blob.data_stream.read().decode(
                    encoding="utf-8", errors="ignore")  # Suponiendo que la codificación es Latin-1
            except UnicodeDecodeError:
                try:
                    contenido_archivo = blob.data_stream.read().decode(encoding="utf-8", errors="ignore")
                except UnicodeDecodeError:
                    print(f"Error de decodificación: {blob.name}")
                    continue

            # Excluir líneas en blanco y comentarios
            lineas_codigo = [linea for linea in contenido_archivo.splitlines() if not re.match(r"^\s*$|^\s*#", linea)]
            contador_lineas += len(lineas_codigo)

            # Contar archivos
            contador_archivos += 1

    # Devolver el recuento total
    return contador_lineas


contador_lineas = contar_lineas_codigo(repo_path)

print(f"Recuento total de líneas de código: {contador_lineas}")

# Obtener lineas modificadas
log = repo.git.diff()
print(f"\nTotal de líneas de código modificadas: {log}")

# Analizar commits por archivo/directorio
commits_por_ruta = defaultdict(int)
for commit in repo.iter_commits():
    for archivo in commit.stats.files:
        ruta = archivo.split('/')
        directorio = '/'.join(ruta[:-1])
        commits_por_ruta[directorio] += 1

# Identificar zonas con más probabilidad de deuda técnica
print("\nZonas con más probabilidad de deuda técnica (basado en cantidad de commits):")
zonas_deuda_tecnica = sorted(commits_por_ruta.items(), key=lambda x: x[1], reverse=True)[:5]
for zona, commits in zonas_deuda_tecnica:
    print(f"{zona}: {commits} commits")

# Calcular edad promedio de los commits
edades_commits = [commit.committed_date for commit in repo.iter_commits()]
edad_promedio = sum(edades_commits) / len(edades_commits)
print(f"\nEdad promedio de los commits: {edad_promedio}")
