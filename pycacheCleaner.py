import os
import shutil

def clean_python_cache(root_dir: str = ".") -> None:
    """Supprime tous les dossiers __pycache__ et fichiers .pyc dans le projet."""
    removed_dirs = 0
    removed_files = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Supprime __pycache__ si présent
        if "__pycache__" in dirnames:
            cache_dir = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(cache_dir)
            removed_dirs += 1
            dirnames.remove("__pycache__")  # pour ne pas parcourir dedans

        # Supprime tous les .pyc
        for f in filenames:
            if f.endswith(".pyc"):
                file_path = os.path.join(dirpath, f)
                os.remove(file_path)
                removed_files += 1

    print(f"✅ Supprimé {removed_dirs} dossiers __pycache__ et {removed_files} fichiers .pyc")

# Utilisation
if __name__ == "__main__":
    clean_python_cache()