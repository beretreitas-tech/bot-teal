# Grupo Teal — WhatsApp Bot

Servidor Flask que envía presupuestos por WhatsApp via Twilio.

## Variables de entorno en Railway
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN  
- TWILIO_WA_FROM (ej: whatsapp:+14155238886)
- PUBLIC_URL (ej: https://teal-bot.railway.app)

## Endpoint
POST /send
{
  "to": "595981234567",
  "message": "texto del presupuesto",
  "pdf": "base64...",
  "filename": "PRESUPUESTO-260088.pdf"
}
