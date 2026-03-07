# Integração Marcha Pay (PIX) – Animacase

Para gerar PIX de verdade (em vez do mock), use o backend com Marcha Pay.

## 1. Instalar dependências

```bash
npm install
```

## 2. Configurar variáveis de ambiente

Copie o exemplo e preencha com suas chaves da Marcha Pay:

```bash
cp .env.example .env
```

Edite `.env` e defina:

- **MARCHABB_PUBLIC_KEY** – chave pública (painel Marcha Pay)
- **MARCHABB_SECRET_KEY** – chave secreta (painel Marcha Pay)
- **SITE_URL** – URL do site (ex.: `https://seusite.com.br` ou em dev `http://localhost:3000`)

(Opcional) **UTMIFY_API_TOKEN** – para enviar pedidos ao Utmify.

## 3. Subir o servidor

```bash
npm start
```

O site fica em **http://localhost:3000**. Abra o checkout por essa URL (não por `file://`) para que as chamadas `/api/create-pix` e `/api/pix-status` funcionem.

## Fluxo

1. No checkout, o cliente escolhe PIX e clica em **Ir para Mercado Pago**.
2. Na tela **Revise o seu pagamento**, ao clicar em **Criar Pix**, o front envia `POST /api/create-pix` com os dados do pedido.
3. O servidor chama a API da Marcha Pay e devolve `qrcode` e `transactionId`.
4. A página **Pix gerado** exibe o QR Code e faz polling em `GET /api/pix-status/:transactionId` até o status ser `paid`.
5. Quando o pagamento é aprovado na Marcha Pay, o servidor pode receber o webhook em `POST /api/webhook-pix` e o polling na página detecta `paid` e redireciona para **Pagamento aprovado**.

## Documentação Marcha Pay

- API: `https://api.marchabb.com/v1/transactions`
- Autenticação: Basic (PUBLIC_KEY:SECRET_KEY em base64)
- Payload de criação: `amount` (centavos), `currency: 'BRL'`, `paymentMethod: 'pix'`, `items`, `customer` (name, email, document.number, phone).
