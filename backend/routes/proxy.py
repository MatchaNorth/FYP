from flask import Blueprint, request, Response
import requests

proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route('/steam', methods=['GET'])
def steam_proxy():
    url = request.args.get('url')
    if not url:
        return {'error': 'No URL provided'}, 400
    
    try:
        # 添加 Steam 特定的 headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        return response.text
    except Exception as e:
        return {'error': str(e)}, 500 