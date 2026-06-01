from pathlib import Path

from flask import Blueprint, jsonify, send_from_directory


docs_bp = Blueprint('docs_bp', __name__)


ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / 'docs'
DOCS_ASSETS_DIR = DOCS_DIR / 'assets'
LANG_DOC_MAP = {
    'es': 'GUIA_USUARIO.md',
    'en': 'USER_GUIDE.md',
}


@docs_bp.route('/docs/<lang>', methods=['GET'])
def get_documentation(lang):
    normalized_lang = (lang or '').strip().lower()
    doc_name = LANG_DOC_MAP.get(normalized_lang)
    if doc_name is None:
        return jsonify({'error': 'Invalid language. Use "es" or "en".'}), 400

    doc_path = DOCS_DIR / doc_name
    if not doc_path.exists():
        return jsonify({'error': f'Documentation not found: {doc_name}'}), 404

    try:
        content = doc_path.read_text(encoding='utf-8')
    except Exception as exc:  # pragma: no cover - defensive branch
        return jsonify({'error': f'Failed to read documentation: {exc}'}), 500

    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@docs_bp.route('/docs/assets/<path:filename>', methods=['GET'])
def get_documentation_asset(filename):
    return send_from_directory(DOCS_ASSETS_DIR, filename)
