from flask import Flask, request, jsonify, render_template, send_from_directory
import logging
import os
from scrape import scrape_website
from parse import parse_content
from api import query_ai_models, MODEL_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-secret-key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Static file routes
@app.route('/')
@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('templates', 'dashboard.html')

@app.route('/login.html')
def login():
    return send_from_directory('templates', 'login.html')

@app.route('/index.html')
def main_app():
    return send_from_directory('templates', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('templates', 'style.css')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape website endpoint"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        logger.info(f"Scraping URL: {url}")
        
        # Scrape the website
        html_content = scrape_website(url)
        if html_content is None:
            return jsonify({'error': 'Failed to scrape website. Please check the URL and try again.'}), 400
        
        # Parse the content
        parsed_content = parse_content(html_content)
        
        logger.info(f"Successfully scraped and parsed content from: {url}")
        return jsonify(parsed_content)
    
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/ask', methods=['POST'])
def ask():
    """Ask AI models endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        question = data.get('question', '').strip()
        context = data.get('context', {})
        model = data.get('model', 'gemini').lower()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not context:
            return jsonify({'error': 'Context is required'}), 400
        
        if model not in MODEL_CONFIG:
            return jsonify({'error': f'Invalid model. Available models: {list(MODEL_CONFIG.keys())}'}), 400
        
        logger.info(f"Processing question with {model} model: {question[:100]}...")
        
        # Query the specific AI model
        from api import query_openrouter
        response = query_openrouter(question, context, model)
        
        return jsonify({'answer': response})
    
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/ask-all', methods=['POST'])
def ask_all():
    """Ask all AI models endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        question = data.get('question', '').strip()
        context = data.get('context', {})
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not context:
            return jsonify({'error': 'Context is required'}), 400
        
        logger.info(f"Processing question with all models: {question[:100]}...")
        
        # Query all AI models
        responses = query_ai_models(question, context)
        
        return jsonify(responses)
    
    except Exception as e:
        logger.error(f"Error in ask-all endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    try:
        models = {
            model_key: {
                'name': config['name'],
                'color': config['color'],
                'model': config['model']
            }
            for model_key, config in MODEL_CONFIG.items()
        }
        return jsonify(models)
    
    except Exception as e:
        logger.error(f"Error in models endpoint: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_available': list(MODEL_CONFIG.keys()),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check required environment variables
    required_vars = ['OPENROUTER_API_KEY', 'FLASK_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
        exit(1)
    
    logger.info("Starting AI Web Scraper Flask application...")
    logger.info(f"Available AI models: {', '.join(MODEL_CONFIG.keys())}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)