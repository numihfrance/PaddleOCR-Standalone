# ============================================================
# PATCH CITRIX : Corriger Path.home() sous Nuitka
# Nuitka retourne le répertoire de l'exe au lieu de USERPROFILE.
# Ce patch doit être appliqué AVANT tout import de paddleocr/paddlex.
# ============================================================
import os
import pathlib

def _get_user_home():
    """Retourne le vrai répertoire home de l'utilisateur courant."""
    # USERPROFILE = standard Windows (C:\Users\<login>)
    # HOME = fallback Unix/MSYS
    home = (
        os.environ.get("USERPROFILE")
        or os.environ.get("HOME")
        or os.path.expanduser("~")
    )
    return pathlib.Path(home)

# Monkey-patch Path.home() pour retourner le bon répertoire
_fixed_home = _get_user_home()
pathlib.Path.home = classmethod(lambda cls: _fixed_home)

# Forcer PADDLEX_HOME vers le répertoire de l'utilisateur
# (sera sous C:\Users\<login>\.paddlex — chaque user a le sien)
if "PADDLEX_HOME" not in os.environ:
    os.environ["PADDLEX_HOME"] = str(_fixed_home / ".paddlex")

# Pré-créer les sous-répertoires nécessaires
_paddlex_home = pathlib.Path(os.environ["PADDLEX_HOME"])
(_paddlex_home / "temp").mkdir(parents=True, exist_ok=True)
(_paddlex_home / "official_models").mkdir(parents=True, exist_ok=True)
# ============================================================
# FIN DU PATCH
# ============================================================

# Compilation instructions
# nuitka-project: --standalone

# nuitka-project: --include-package-data=paddleocr
# nuitka-project: --include-package-data=paddlex

# nuitka-project-if: {OS} == "Windows":
#     nuitka-project: --output-filename=paddleocr
# nuitka-project-if: {OS} == "Linux":
#     nuitka-project: --output-filename=paddleocr.bin

# nuitka-project: --include-distribution-metadata=imagesize
# nuitka-project: --include-distribution-metadata=opencv-contrib-python
# nuitka-project: --include-distribution-metadata=pyclipper
# nuitka-project: --include-distribution-metadata=pypdfium2
# nuitka-project: --include-distribution-metadata=python-bidi
# nuitka-project: --include-distribution-metadata=shapely


# Windows-specific metadata for the executable
# nuitka-project-if: {OS} == "Windows":
#     nuitka-project: --file-description="PaddleOCR Standalone Executable"
#     nuitka-project: --file-version="1.4.0"
#     nuitka-project: --product-name="PaddleOCR-CPU"
#     nuitka-project: --product-version="1.4.0"
#     nuitka-project: --copyright="timminator"
#     nuitka-project: --windows-icon-from-ico=paddleocr.ico


import sys
import os

# os.environ["PADDLE_PDX_CACHE_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".paddlex")
os.environ["PADDLE_PDX_CACHE_HOME"] = str(_fixed_home / ".paddlex")

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from paddleocr.__main__ import console_entry

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    console_entry()
