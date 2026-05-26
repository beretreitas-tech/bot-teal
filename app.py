from flask import Flask, request, jsonify, Response
from twilio.rest import Client
import os, base64, uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')
FROM_WA     = os.environ.get('TWILIO_WA_FROM')
PUBLIC_URL  = os.environ.get('PUBLIC_URL')

client = Client(ACCOUNT_SID, AUTH_TOKEN)
pdf_store = {}

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Grupo Teal WA Bot'})

@app.route('/pdf/<pid>')
def serve_pdf(pid):
    if pid not in pdf_store:
        return 'Not found', 404
    return Response(
        base64.b64decode(pdf_store[pid]['data']),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{pdf_store[pid]["name"]}"'}
    )

@app.route('/send', methods=['POST'])
def send_whatsapp():
    data = request.get_json()
    to_number = data.get('to')
    pdf_b64   = data.get('pdf')
    pdf_name  = data.get('filename', 'presupuesto.pdf')

    if not to_number:
        return jsonify({'error': 'Falta número de destino'}), 400

    to_wa = f'whatsapp:+{to_number.lstrip("+")}'

    try:
        pid = str(uuid.uuid4())
        pdf_store[pid] = {'data': pdf_b64, 'name': pdf_name}
        pdf_url = f'{PUBLIC_URL}/pdf/{pid}'

        # Send ONLY the PDF, no text body
        msg = client.messages.create(
            from_=FROM_WA,
            to=to_wa,
            body='',
            media_url=[pdf_url]
        )

        return jsonify({'success': True, 'sid': msg.sid})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
