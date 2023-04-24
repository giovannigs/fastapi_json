from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import os
from datetime import datetime

app = FastAPI()
security = HTTPBasic()

# Definir um dicionário de nomes de usuários e senhas
users = {
    'user1': 'password1',
    'user2': 'password2'
}

# Definir a função de autenticação
async def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if username not in users or password != users[username]:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    return username

# Aplicar autenticação ao terminal da API
@app.post('/lnd/api/sap/{table_name}')
async def receive_json(table_name: str, request: Request, username: str = Depends(authenticate)):
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")
    try:
        data = await request.json()
        # Verifica se o corpo da requisição é um JSON válido
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O corpo da requisição deve estar em formato JSON")

        # Cria o diretório no caminho específico para cada 'table_name'
        table_dir = os.path.join(os.getcwd(),'lnd/api/sap/',table_name)
        os.makedirs(table_dir, exist_ok=True)
        filename = os.path.join(table_dir, f'{table_name}_{dt_string}.json')

        # Salva os dados em um arquivo JSON
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return f'JSON salvo: {filename}'

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)