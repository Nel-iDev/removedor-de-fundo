# Removedor de Fundo

Sprint 2 da API web em Flask. O upload é processado inteiramente em memória e retorna um PNG com transparência.

A rota aceita imagens PNG, JPEG e WEBP de até 16 MB no campo `arquivo`.

## Instalar

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

A primeira execução pode baixar o modelo do `rembg`. Por padrão, o projeto usa `u2netp` para reduzir o consumo de memória.

## Executar o servidor

```powershell
python app.py
```

A API ficará disponível em `http://127.0.0.1:5000`. Também é possível iniciar com `flask --app app run --debug`.

## Testar a remoção

```powershell
curl.exe -X POST -F "arquivo=@C:\caminho\imagem.jpg" http://127.0.0.1:5000/remover-fundo --output resultado.png
```

Respostas de erro retornam JSON: `400` para arquivo ausente ou corrompido, `413` para upload grande e `415` para formato não suportado.
