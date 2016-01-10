#!/usr/bin/env python
import os
from swampdragon.swampdragon_server import run_server

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_dietas.settings")

run_server()

'''
#!/usr/bin/env python
import os
import sys


from swampdragon.swampdragon_server import run_server

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "<project>.settings")

host_port = sys.argv[1] if len(sys.argv) > 1 else None

run_server(host_port=host_port)
'''