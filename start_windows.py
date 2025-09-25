# -*- coding: utf-8 -*-
import os
import sys

# Configuration de l'encodage pour Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    # Définir la page de code UTF-8
    os.system('chcp 65001 >nul 2>&1')

# Importer le script principal
from start import main

if __name__ == "__main__":
    main()