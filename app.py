import argparse
import io
import os
from functools import lru_cache
from pathlib import Path

import rembg
from flask import Flask, jsonify, request, send_file
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
MODEL_NAME = os.getenv("REMBG_MODEL", "u2netp")


@lru_cache(maxsize=1)
def _get_rembg_session():
    return rembg.new_session(MODEL_NAME)


def _remove_background_bytes(image_data: bytes) -> bytes:
    result = rembg.remove(image_data, session=_get_rembg_session())
    with Image.open(io.BytesIO(result)) as image:
        output = io.BytesIO()
        image.convert("RGBA").save(output, format="PNG")
    return output.getvalue()


def remove_background(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    source = Path(input_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Imagem de entrada não encontrada: {source}")

    if output_path is None:
        destination = source.with_name(f"{source.stem}_sem_fundo.png")
    else:
        destination = Path(output_path).expanduser().resolve()
        if destination.suffix.lower() != ".png":
            destination = destination.with_suffix(".png")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(_remove_background_bytes(source.read_bytes()))
    return destination


@app.get("/saude")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/api/remover-fundo")
def remove_background_api():
    uploaded_file = request.files.get("arquivo")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"erro": "Envie uma imagem no campo 'arquivo'."}), 400

    try:
        image_data = uploaded_file.read()
        if not image_data:
            return jsonify({"erro": "O arquivo enviado está vazio."}), 400
        output_data = _remove_background_bytes(image_data)
    except Exception:
        app.logger.exception("Não foi possível processar a imagem enviada.")
        return jsonify({"erro": "Não foi possível processar a imagem."}), 500

    safe_name = secure_filename(uploaded_file.filename) or "imagem"
    download_name = f"{Path(safe_name).stem}.png"
    return send_file(
        io.BytesIO(output_data),
        mimetype="image/png",
        as_attachment=True,
        download_name=download_name,
    )


@app.errorhandler(413)
def payload_too_large(_error):
    return jsonify({"erro": "A imagem excede o limite de 16 MB."}), 413


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove o fundo de uma imagem e salva o resultado em PNG."
    )
    parser.add_argument("entrada", type=Path, help="Caminho da imagem de entrada.")
    parser.add_argument("saida", type=Path, nargs="?", help="Caminho do PNG de saída.")
    args = parser.parse_args()

    try:
        result = remove_background(args.entrada, args.saida)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.exit(1, f"Erro: {error}\n")

    print(f"Imagem salva em: {result}")


if __name__ == "__main__":
    main()
