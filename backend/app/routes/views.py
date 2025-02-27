from flask import jsonify
from app.routes import api_bp

@api_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Hello from Flask!'})