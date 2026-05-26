from flask import Flask, request, jsonify
from twilio.rest import Client
import os, base64, tempfile, uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN')
FROM_WA     = os.environ.get('TWILIO_WA_FROM')   # whatsapp:+14155238886
PUBLIC_URL  = os.environ.get('PUBLIC_URL')         # tu URL de Railway

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Temporary store for PDFs (in-memory, served via /pdf/<id>)
pdf_store = {}

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'Grupo Teal WA Bot'})

@app.route('/pdf/<pid>')
def serve_pdf(pid):
    from flask import Response
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
    to_number   = data.get('to')       # e.g. "595981234567"
    message_txt = data.get('message')  # resumen del presupuesto
    pdf_b64     = data.get('pdf')      # PDF en base64
    pdf_name    = data.get('filename', 'presupuesto.pdf')

    if not to_number or not message_txt:
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    to_wa = f'whatsapp:+{to_number.lstrip("+")}'

    try:
        msg_params = {
            'from_': FROM_WA,
            'to':    to_wa,
            'body':  message_txt,
        }

        # If PDF provided, store it and attach as media
        if pdf_b64:
            pid = str(uuid.uuid4())
            pdf_store[pid] = {'data': pdf_b64, 'name': pdf_name}
            pdf_url = f'{PUBLIC_URL}/pdf/{pid}'
            msg_params['media_url'] = [pdf_url]

        msg = client.messages.create(**msg_params)

        return jsonify({'success': True, 'sid': msg.sid})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
