from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    # Lakukan scraping sesuai URL (misalnya, ambil konten dari URL)
    # Kembalikan data yang di-scrape (contoh placeholder)
    scraped_content = "This is scraped content from " + url
    return jsonify({"content": scraped_content})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')
    content = data.get('content')
    model = data.get('model', 'Gemini')  # Default model adalah Gemini

    # Logika untuk memproses pertanyaan dengan model yang dipilih
    # (misalnya, panggil model Gemini, Ollama, atau Deepseek)
    answer = f"Answer from {model} based on the content: {content}"
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
