# Removedor de Fundo

Sprint 1 do backend em Python, usando Flask, `rembg` e Pillow para gerar imagens PNG com transparência.

## Instalar

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

A primeira execução pode baixar o modelo usado pelo `rembg`. Por padrão, o projeto usa `u2netp` para reduzir o consumo de memória; para escolher outro modelo compatível, defina `REMBG_MODEL` antes de executar.

## Testar pelo terminal

```powershell
python app.py "C:\caminho\imagem.jpg" "resultado.png"
```

Se o caminho de saída for omitido, o arquivo será salvo ao lado da entrada com o sufixo `_sem_fundo.png`.

## Testar a API Flask

```powershell
flask --app app run --debug
```

Em outro terminal, envie a imagem e salve a resposta:

```powershell
curl.exe -X POST -F "arquivo=@C:\caminho\imagem.jpg" http://127.0.0.1:5000/api/remover-fundo --output resultado.png
```
