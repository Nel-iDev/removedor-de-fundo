# Removedor de Fundo

Sprint 3 da aplicação web completa. A interface em Flask recebe a imagem, exibe o carregamento e oferece comparação e download do resultado.

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

A interface e a API ficarão disponíveis em `http://127.0.0.1:5000`. Abra esse endereço no navegador após iniciar o servidor. Também é possível iniciar com `flask --app app run --debug`.

## Testar a remoção

```powershell
curl.exe -X POST -F "arquivo=@C:\caminho\imagem.jpg" http://127.0.0.1:5000/remover-fundo --output resultado.png
```

Respostas de erro retornam JSON: `400` para arquivo ausente ou corrompido, `413` para upload grande e `415` para formato não suportado.
