#!/bin/bash
cd /home/abemelek-samson/Abemelek_Folder/agency/stepin/backend
export PYTHONPATH=$PYTHONPATH:/home/abemelek-samson/Abemelek_Folder/agency/stepin/backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8002
