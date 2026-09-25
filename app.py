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
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_PIXELS = 40_000_000


class InvalidImageData(ValueError):
    pass


class UnsupportedImageFormat(ValueError):
    pass


@lru_cache(maxsize=1)
def _get_rembg_session():
    return rembg.new_session(MODEL_NAME)


def _validate_image(image_data: bytes, filename: str) -> None:
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise UnsupportedImageFormat

    try:
        with Image.open(io.BytesIO(image_data)) as image:
            image_format = (image.format or "").upper()
            if image_format not in ALLOWED_FORMATS:
                raise UnsupportedImageFormat
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise InvalidImageData("A imagem possui dimensões grandes demais.")
            image.verify()
        with Image.open(io.BytesIO(image_data)) as image:
            image.load()
    except UnsupportedImageFormat:
        raise
    except (
        Image.DecompressionBombError,
        OSError,
        SyntaxError,
        ValueError,
    ) as error:
        raise InvalidImageData(
            "O arquivo enviado não contém uma imagem válida."
        ) from error


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


@app.post("/remover-fundo")
@app.post("/api/remover-fundo")
def remove_background_api():
    uploaded_file = request.files.get("arquivo")
    if uploaded_file is None:
        uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"erro": "Envie uma imagem no campo 'arquivo' ou 'file'."}), 400

    image_data = uploaded_file.read()
    if not image_data:
        return jsonify({"erro": "O arquivo enviado está vazio."}), 400

    try:
        _validate_image(image_data, uploaded_file.filename)
    except UnsupportedImageFormat:
        return jsonify(
            {"erro": "Formato inválido. Envie uma imagem PNG, JPEG ou WEBP."}
        ), 415
    except InvalidImageData as error:
        return jsonify({"erro": str(error)}), 400

    try:
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
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
