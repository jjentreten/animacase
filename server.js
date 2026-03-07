/**
 * Backend Animacase (gocase-clone)
 * Serve arquivos estáticos e integração Marcha Pay (PIX).
 * Configure MARCHABB_PUBLIC_KEY e MARCHABB_SECRET_KEY no .env
 */
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

const MARCHABB_URL = 'https://api.marchabb.com/v1/transactions';
const MARCHABB_GET_URL = 'https://api.marchabb.com/v1/transactions';
const PUBLIC_KEY = (process.env.MARCHABB_PUBLIC_KEY || '').trim();
const SECRET_KEY = (process.env.MARCHABB_SECRET_KEY || '').trim();
const SITE_URL = (process.env.SITE_URL || 'http://localhost:' + PORT).replace(/\/$/, '');

const UTMIFY_URL = 'https://api.utmify.com.br/api-credentials/orders';
const UTMIFY_TOKEN = (process.env.UTMIFY_API_TOKEN || '').trim();
const PENDING_ORDERS_FILE = path.join(__dirname, 'data', 'pending-utmify-orders.json');
const POLL_INTERVAL_MS = 10 * 1000;

app.use(cors());
app.use(express.json());

function ensureDataDir() {
  const dir = path.join(__dirname, 'data');
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function readPendingOrders() {
  ensureDataDir();
  try {
    const raw = fs.readFileSync(PENDING_ORDERS_FILE, 'utf8');
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : [];
  } catch (_) {
    return [];
  }
}

function writePendingOrders(list) {
  ensureDataDir();
  fs.writeFileSync(PENDING_ORDERS_FILE, JSON.stringify(list, null, 0), 'utf8');
}

function toUtcDateTime(date) {
  const d = date instanceof Date ? date : new Date(date);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, '0');
  const day = String(d.getUTCDate()).padStart(2, '0');
  const h = String(d.getUTCHours()).padStart(2, '0');
  const min = String(d.getUTCMinutes()).padStart(2, '0');
  const s = String(d.getUTCSeconds()).padStart(2, '0');
  return y + '-' + m + '-' + day + ' ' + h + ':' + min + ':' + s;
}

function buildUtmifyPayload(opts) {
  const {
    orderId,
    status,
    createdAt,
    approvedDate,
    refundedAt,
    customer,
    products,
    trackingParameters,
    totalPriceInCents
  } = opts;
  const gatewayFeeInCents = Math.round(totalPriceInCents * 0.01) || 0;
  const userCommissionInCents = Math.max(1, totalPriceInCents - gatewayFeeInCents);
  return {
    orderId: String(orderId),
    platform: 'Animacase',
    paymentMethod: 'pix',
    status,
    createdAt,
    approvedDate: approvedDate || null,
    refundedAt: refundedAt || null,
    customer: {
      name: customer.name,
      email: customer.email,
      phone: customer.phone || null,
      document: customer.document || null,
      country: customer.country || 'BR',
      ip: customer.ip || '0.0.0.0'
    },
    products: products.map((p) => ({
      id: String(p.id || p.externalRef || p.name),
      name: p.name,
      planId: null,
      planName: null,
      quantity: p.quantity || 1,
      priceInCents: p.priceInCents
    })),
    trackingParameters: {
      src: trackingParameters?.src ?? null,
      sck: trackingParameters?.sck ?? null,
      utm_source: trackingParameters?.utm_source ?? null,
      utm_campaign: trackingParameters?.utm_campaign ?? null,
      utm_medium: trackingParameters?.utm_medium ?? null,
      utm_content: trackingParameters?.utm_content ?? null,
      utm_term: trackingParameters?.utm_term ?? null
    },
    commission: {
      totalPriceInCents,
      gatewayFeeInCents,
      userCommissionInCents
    }
  };
}

async function sendToUtmify(payload) {
  if (!UTMIFY_TOKEN) return;
  try {
    const res = await fetch(UTMIFY_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-token': UTMIFY_TOKEN
      },
      body: JSON.stringify(payload)
    });
    const text = await res.text();
    if (!res.ok) console.error('Utmify erro', res.status, text);
    else console.log('Utmify: pedido', payload.orderId, 'enviado com status', payload.status);
  } catch (err) {
    console.error('Utmify erro ao enviar:', err.message);
  }
}

// Servir arquivos estáticos (index.html, checkout.html, etc.)
app.use(express.static(path.join(__dirname)));

/**
 * POST /api/create-pix
 * Cria transação PIX na Marcha Pay.
 * Payload Animacase: { total, items: [{ name, priceSale?, price?, quantity }], customer: { email, firstName, lastName?, cpf, phone? }, trackingParameters? }
 */
app.post('/api/create-pix', async (req, res) => {
  if (!PUBLIC_KEY || !SECRET_KEY) {
    return res.status(500).json({
      success: false,
      error: 'Chaves da API Marcha Pay não configuradas. Configure MARCHABB_PUBLIC_KEY e MARCHABB_SECRET_KEY no .env'
    });
  }

  const { amount, total, items, customer: rawCustomer, trackingParameters } = req.body;

  let amountCentavos = typeof amount === 'number' ? Math.round(amount) : 0;
  if (amountCentavos < 1 && typeof total === 'number') {
    amountCentavos = Math.round(Number(total) * 100);
  }
  if (amountCentavos < 1) {
    return res.status(400).json({ success: false, error: 'Valor inválido (amount ou total)' });
  }

  if (!items || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ success: false, error: 'Lista de itens obrigatória' });
  }

  // Normalizar cliente: Animacase envia firstName + lastName; Marcha Pay espera name
  const customerName = rawCustomer?.name ||
    [rawCustomer?.firstName, rawCustomer?.lastName].filter(Boolean).join(' ').trim() ||
    rawCustomer?.firstName ||
    '';
  if (!customerName || !rawCustomer?.email) {
    return res.status(400).json({ success: false, error: 'Cliente obrigatório (nome e e-mail)' });
  }

  const docNumber = (rawCustomer?.document?.number || rawCustomer?.cpf || '').replace(/\D/g, '');
  if (!docNumber || docNumber.length < 11) {
    return res.status(400).json({ success: false, error: 'CPF do cliente obrigatório' });
  }

  const phone = '11999999999';

  const payload = {
    amount: amountCentavos,
    currency: 'BRL',
    paymentMethod: 'pix',
    items: items.map((item) => {
      const price = item.unitPrice ?? item.price ?? item.priceSale ?? 0;
      const priceNum = Number(price);
      const unitPrice = priceNum < 100 ? Math.round(priceNum * 100) : Math.round(priceNum);
      return {
        title: item.title || item.name || 'Produto',
        unitPrice,
        quantity: item.quantity || 1,
        tangible: item.tangible !== false,
        externalRef: item.externalRef || item.id || item.name
      };
    }),
    customer: {
      name: customerName.trim(),
      email: rawCustomer.email.trim(),
      phone,
      document: {
        number: docNumber,
        type: rawCustomer?.document?.type || 'cpf'
      }
    },
    externalRef: 'animacase-' + Date.now()
  };

  if (SITE_URL) {
    payload.postbackUrl = SITE_URL + '/api/webhook-pix';
    payload.returnUrl = SITE_URL + '/checkout-pix-gerado.html?status=return';
  }

  const auth = 'Basic ' + Buffer.from(PUBLIC_KEY + ':' + SECRET_KEY).toString('base64');

  try {
    const response = await fetch(MARCHABB_URL, {
      method: 'POST',
      headers: {
        Authorization: auth,
        'Content-Type': 'application/json',
        Accept: 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        success: false,
        error: data.message || data.error || 'Erro ao criar transação PIX'
      });
    }

    const pix = data.pix || data.data?.pix;
    const secureUrl = data.secureUrl || data.data?.secureUrl;
    const qrcode = pix?.qrcode || pix?.copyPaste || '';

    if (!qrcode && !secureUrl) {
      return res.status(500).json({
        success: false,
        error: 'Resposta da Marcha Pay sem QR Code PIX'
      });
    }

    const transactionId = data.id ?? data.data?.id ?? data.objectId;

    if (UTMIFY_TOKEN && transactionId != null) {
      const clientIp = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || req.socket?.remoteAddress || req.ip || '0.0.0.0';
      const ip = clientIp.replace(/^::ffff:/, '');
      const productsForUtmify = items.map((item) => {
        const price = item.unitPrice ?? item.price ?? item.priceSale ?? 0;
        const priceNum = Number(price);
        const priceInCents = priceNum < 100 ? Math.round(priceNum * 100) : Math.round(priceNum);
        return {
          id: item.id || item.externalRef || item.name,
          name: item.name || item.title || 'Produto',
          quantity: item.quantity || 1,
          priceInCents
        };
      });
      const createdAt = toUtcDateTime(new Date());
      const utmifyPayload = buildUtmifyPayload({
        orderId: String(transactionId),
        status: 'waiting_payment',
        createdAt,
        approvedDate: null,
        refundedAt: null,
        customer: {
          name: customerName.trim(),
          email: rawCustomer.email.trim(),
          phone,
          document: docNumber,
          country: 'BR',
          ip
        },
        products: productsForUtmify,
        trackingParameters: trackingParameters || {},
        totalPriceInCents: amountCentavos
      });
      await sendToUtmify(utmifyPayload);
      const pending = readPendingOrders();
      pending.push({ transactionId: String(transactionId), createdAt, utmifyPayload, provider: 'marchapay' });
      writePendingOrders(pending);
    }

    return res.json({
      success: true,
      transactionId,
      secureUrl: secureUrl || null,
      qrcode: qrcode || '',
      amount: amountCentavos
    });
  } catch (err) {
    console.error('Erro Marcha Pay:', err);
    return res.status(500).json({
      success: false,
      error: err.message || 'Erro ao conectar com o gateway de pagamento'
    });
  }
});

/**
 * GET /api/pix-status/:transactionId
 * Consulta status da transação na Marcha Pay.
 */
app.get('/api/pix-status/:transactionId', async (req, res) => {
  const { transactionId } = req.params;
  if (!transactionId) return res.status(400).json({ status: 'unknown' });

  if (!PUBLIC_KEY || !SECRET_KEY) {
    return res.json({ status: 'unknown' });
  }

  try {
    const auth = 'Basic ' + Buffer.from(PUBLIC_KEY + ':' + SECRET_KEY).toString('base64');
    const response = await fetch(MARCHABB_GET_URL + '/' + encodeURIComponent(transactionId), {
      method: 'GET',
      headers: { Authorization: auth, Accept: 'application/json' }
    });
    const data = response.ok ? await response.json() : null;
    const status = data?.status ?? data?.data?.status ?? 'unknown';
    return res.json({
      status: status === 'paid' || status === 'approved' ? 'paid' : 'pending'
    });
  } catch (err) {
    console.error('pix-status Marcha:', err.message);
    return res.status(500).json({ status: 'unknown' });
  }
});

/**
 * POST /api/webhook-pix
 * Webhook recebido pela Marcha Pay (postback de status).
 */
app.post('/api/webhook-pix', (req, res) => {
  const body = req.body;
  console.log('Webhook Marcha Pay:', body?.type, body?.objectId, body?.data?.status);
  res.status(200).send('OK');
});

/**
 * Polling: atualizar Utmify quando transação Marcha Pay for paga
 */
async function pollMarchaAndUpdateUtmify() {
  if (!PUBLIC_KEY || !SECRET_KEY || !UTMIFY_TOKEN) return;
  const pending = readPendingOrders().filter((p) => !p.provider || p.provider === 'marchapay');
  if (pending.length === 0) return;

  const auth = 'Basic ' + Buffer.from(PUBLIC_KEY + ':' + SECRET_KEY).toString('base64');
  const stillPending = [];

  for (const row of pending) {
    try {
      const resp = await fetch(MARCHABB_GET_URL + '/' + encodeURIComponent(row.transactionId), {
        method: 'GET',
        headers: { Authorization: auth, Accept: 'application/json' }
      });
      const data = resp.ok ? await resp.json() : null;
      const status = data?.status ?? data?.data?.status;

      if (status === 'paid' || status === 'approved') {
        const paidAt = data?.paidAt ?? data?.data?.paidAt;
        const approvedDate = paidAt ? toUtcDateTime(new Date(paidAt)) : toUtcDateTime(new Date());
        const payload = { ...row.utmifyPayload, status: 'paid', approvedDate };
        await sendToUtmify(payload);
        console.log('Utmify atualizado: pedido', row.transactionId, 'pago');
      } else {
        stillPending.push(row);
      }
    } catch (err) {
      console.error('Poll Marcha:', row.transactionId, err.message);
      stillPending.push(row);
    }
  }

  if (stillPending.length !== pending.length) {
    const all = readPendingOrders();
    const others = all.filter((p) => p.provider && p.provider !== 'marchapay');
    writePendingOrders([...others, ...stillPending]);
  }
}

let pollTimer = null;
function startPolling() {
  if (pollTimer) return;
  pollMarchaAndUpdateUtmify();
  pollTimer = setInterval(pollMarchaAndUpdateUtmify, POLL_INTERVAL_MS);
}

app.listen(PORT, () => {
  console.log('Animacase rodando em http://localhost:' + PORT);
  if (PUBLIC_KEY && SECRET_KEY) {
    console.log('PIX: Marcha Pay ativo.');
    if (UTMIFY_TOKEN) {
      console.log('Utmify: token configurado - pedidos serão enviados ao painel.');
      startPolling();
    }
  } else {
    console.warn('AVISO: Marcha Pay não configurado. Defina MARCHABB_PUBLIC_KEY e MARCHABB_SECRET_KEY no .env');
  }
});
