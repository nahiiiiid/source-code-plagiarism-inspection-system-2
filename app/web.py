from flask import Flask, request, render_template, jsonify
from .config import Config
from .engine.scorer import HybridScorer
from .engine.explain import highlight_similar_regions
import os

def allowed_file(filename: str) -> bool:
    if '.' not in filename:
        return False
    ext = '.' + filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    scorer = HybridScorer(Config.MODEL_NAME, device=Config.DEVICE, topk_matches=Config.TOPK_CHUNK_MATCHES)

    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')

    @app.route('/compare', methods=['POST'])
    def compare():
        f1 = request.files.get('file1')
        f2 = request.files.get('file2')
        if not f1 or not f2:
            return render_template('index.html', error="Please upload both files."), 400
        if not (allowed_file(f1.filename) and allowed_file(f2.filename)):
            return render_template('index.html', error="Unsupported file type."), 400
        if f1.content_length and f1.content_length > app.config['MAX_CONTENT_LENGTH']:
            return render_template('index.html', error="File1 too large."), 400
        if f2.content_length and f2.content_length > app.config['MAX_CONTENT_LENGTH']:
            return render_template('index.html', error="File2 too large."), 400

        code1 = f1.read().decode('utf-8', errors='ignore')
        code2 = f2.read().decode('utf-8', errors='ignore')

        report = scorer.score(code1, code2)
        spans = highlight_similar_regions(code1, code2)

        # thresholding
        suspicious = report['ensemble_score'] >= app.config['SIM_THRESHOLD']

        return render_template('result.html',
                               suspicious=suspicious,
                               threshold=int(app.config['SIM_THRESHOLD']*100),
                               ensemble=round(report['ensemble_score']*100, 2),
                               components={k: round(v*100,2) for k,v in report['components'].items()},
                               chunk_matches=report['chunks']['topk_matches'],
                               spans=spans['spans'],
                               code1=code1,
                               code2=code2)

    @app.route('/api/compare', methods=['POST'])
    def api_compare():
        f1 = request.files.get('file1')
        f2 = request.files.get('file2')
        if not f1 or not f2:
            return jsonify({"error": "Both files required"}), 400
        code1 = f1.read().decode('utf-8', errors='ignore')
        code2 = f2.read().decode('utf-8', errors='ignore')
        report = scorer.score(code1, code2)
        spans = highlight_similar_regions(code1, code2)
        return jsonify({
            "threshold": Config.SIM_THRESHOLD,
            "ensemble_score": report['ensemble_score'],
            "components": report['components'],
            "chunk_matches": report['chunks']['topk_matches'],
            "spans": spans['spans']
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=Config.DEBUG)
