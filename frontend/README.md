# Yaqeen Frontend

Next.js web application for the Yaqeen Islamic digital wallet.

## Stack

- Next.js 16 and React 19
- TypeScript
- Tailwind CSS 4
- SWR for client revalidation
- Prettier for consistent formatting
- Vitest and Testing Library
- Knip for unused-code and dependency analysis

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

The `.env` file and all required values are mandatory. The development and production wrappers fail
immediately when configuration is missing. `DJANGO_API_URL` must resolve to a running Yaqeen
backend.

## Environment

```env
PORT=3003
HOST=127.0.0.1
USE_HTTPS=false

DJANGO_API_URL=http://127.0.0.1:8003
ACCESS_TOKEN_MINUTES=1440
REFRESH_TOKEN_MINUTES=43200
NEXT_PUBLIC_TOAST_DURATION_MS=6000
NEXT_PUBLIC_LOG_LEVEL=info
PAGE_SIZE=10
```

`ACCESS_TOKEN_MINUTES` and `REFRESH_TOKEN_MINUTES` must match the backend. `NEXT_PUBLIC_LOG_LEVEL`
accepts `debug`, `info`, `warn`, or `error`.

## Commands

| Command                | Purpose                                                       |
| ---------------------- | ------------------------------------------------------------- |
| `npm run dev`          | Start the configured development server                       |
| `npm run dev:https`    | Start Next.js development mode with a local HTTPS certificate |
| `npm run build`        | Create and validate the production bundle                     |
| `npm start`            | Start the built custom production server                      |
| `npm run lint`         | Run ESLint                                                    |
| `npm run format`       | Format the codebase with Prettier                             |
| `npm run format:check` | Check formatting without writing changes                      |
| `npm test`             | Run Vitest once                                               |
| `npm run test:watch`   | Run Vitest in watch mode                                      |

Run `npm run build` before `npm start`.

## Production and HTTPS

```bash
npm ci
npm run build
npm start
```

PM2 can start the frontend through the root `ecosystem.config.js`. To enable HTTPS in the custom
production server, set `USE_HTTPS=true` in `frontend/.env` and provide:

- `certificates/localhost-key.pem`
- `certificates/localhost.pem`

In a public deployment, TLS termination at a reverse proxy is generally preferable.

## Application Routes

| Route                                     | Description                                                                  |
| ----------------------------------------- | ---------------------------------------------------------------------------- |
| `/`                                       | Landing page                                                                 |
| `/login`                                  | Sign in                                                                      |
| `/dashboard`                              | Balance, service grid, recent activity, and live notifications               |
| `/send`                                   | Send money by phone or scanned QR code                                       |
| `/receive`                                | Display the user's wallet QR code                                            |
| `/money-requests`                         | Create, accept, and decline money requests                                   |
| `/pay`                                    | Browse and pay verified merchants                                            |
| `/cards`                                  | Add and list wallet cards                                                    |
| `/cards/[id]`                             | View, block, or unblock a card                                               |
| `/recharge`                               | Select a mobile operator                                                     |
| `/recharge/[id]`                          | Purchase airtime or a data pack                                              |
| `/billpay`                                | Browse bill categories                                                       |
| `/billpay/[category]`                     | Browse billers in a category                                                 |
| `/billpay/[category]/[billerId]`          | Pay a bill and pick the bill month                                           |
| `/agents`                                 | Browse verified wallet agents                                                |
| `/banking`                                | Link Islamic bank accounts, add money, withdraw, and view history            |
| `/savings`                                | Browse Mudarabah plans                                                       |
| `/savings/accounts`                       | Open and list savings accounts                                               |
| `/savings/accounts/[account_number]`      | View an account and pay contributions                                        |
| `/loans`                                  | Browse Qard Hasan products                                                   |
| `/loans/apply/[id]`                       | Apply for Qard Hasan financing                                               |
| `/loans/my`                               | View and repay financing                                                     |
| `/remittance`                             | Receive international remittance and view history                            |
| `/tickets`                                | Browse ticket categories and booking history                                 |
| `/tickets/[category]`                     | Browse providers                                                             |
| `/tickets/[category]/[providerId]`        | Select a trip, date, coach, and seats; the total is calculated automatically |
| `/charity`                                | Charity hub                                                                  |
| `/charity/zakat`                          | Calculate Zakat                                                              |
| `/charity/zakat/pay`                      | Pay Zakat to a verified foundation                                           |
| `/charity/zakat/history`                  | View Zakat payment history                                                   |
| `/charity/sadaqah`                        | Browse Sadaqah causes                                                        |
| `/charity/sadaqah/[cause]`                | Browse foundations by cause                                                  |
| `/charity/sadaqah/[cause]/[foundationId]` | Give Sadaqah                                                                 |
| `/charity/sadaqah/history`                | View Sadaqah history                                                         |
| `/charity/sadaqah-jariyah`                | Manage recurring charity                                                     |
| `/charity/hawl`                           | Track Nisab and Hawl eligibility                                             |
| `/rewards`                                | View points, history, and redeem offers                                      |
| `/statements`                             | Generate and review monthly statements                                       |
| `/transactions`                           | Paginated wallet transaction history                                         |
| `/notifications`                          | Notification history and read controls                                       |
| `/support`                                | Create support tickets and reply to conversations                            |
| `/account`                                | Submit KYC and manage nominees                                               |
| `/profile`                                | User, wallet, verification, and card summary                                 |
| `/more`                                   | Mobile overflow navigation                                                   |

## Architecture

- The root protected layout fetches the authenticated profile and initial notifications.
- Server Components fetch initial data directly from Django using the access token cookie.
- Route handlers provide same-origin browser read APIs and attach JWT authorization server-side.
- Server actions perform authenticated mutations and revalidate the shared ledger routes
  (`/dashboard`, `/transactions`, `/notifications`, `/profile`) plus the affected feature route.
- Client lists revalidate through the `useMutateOnSuccess` hook after a mutation succeeds.
- SWR refreshes client data on focus/reconnect and after mutations.
- The dashboard keeps an SSE connection through `/api/notifications/stream`; each event revalidates
  all cached API keys, so lists such as remittance, tickets, and savings refresh without a manual
  reload.
- Amounts and dates use deterministic helpers with South Asian digit grouping and a fixed Asia/Dhaka
  offset, so server and client rendering match.
- The back button and page header take an explicit parent route, so back navigation follows the app
  hierarchy instead of browser history.
- Server-side calls to the Django API go through the Node http/https client in `instrumentation.ts`,
  which avoids a Node fetch parser crash when the backend closes a connection under backpressure.
- Route errors and root layout errors render dedicated boundaries (`app/error.tsx` and
  `app/global-error.tsx`).
- Shared UI primitives such as `Input` and `Select` keep form controls consistent.
- Access and refresh tokens are stored in secure, same-site, HTTP-only cookies.
- List requests send the configured page size; Django enforces its configured maximum.

## Logging

Server-side logs are written under `frontend/logs/` and rotate at 10 MB:

| File        | Content                          |
| ----------- | -------------------------------- |
| `error.log` | Error-level entries              |
| `app.log`   | Debug, info, and warning entries |

Browser logging uses the configured public log level but does not write server log files.

## Quality Checks

```bash
npm run lint
npm run format:check
npm test
npx tsc --noEmit
npx knip --no-progress
npm run build
```

See the [project README](../README.md) for backend setup and PM2 deployment.
