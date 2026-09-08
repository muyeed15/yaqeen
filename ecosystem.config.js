const path = require('path');
const fs = require('fs');

function loadEnv(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`Required environment file not found: ${filePath}`);
  }
  const lines = fs.readFileSync(filePath, 'utf8').split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (!(key in process.env)) process.env[key] = val;
  }
}

function requiredEnv(name) {
  const value = process.env[name];
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`${name} must be set in a service .env file`);
  }
  return value.trim();
}

loadEnv(path.join(__dirname, 'backend', '.env'));
loadEnv(path.join(__dirname, 'frontend', '.env'));

const PORT = requiredEnv('PORT');
const HOST = requiredEnv('HOST');
const BACKEND_PORT = requiredEnv('BACKEND_PORT');
const BACKEND_HOST = requiredEnv('BACKEND_HOST');

function findGunicorn() {
  if (process.env.GUNICORN_PATH && fs.existsSync(process.env.GUNICORN_PATH)) {
    return process.env.GUNICORN_PATH;
  }

  const isWin = process.platform === 'win32';
  const candidate = path.join(
    __dirname,
    'backend',
    '.venv',
    isWin ? 'Scripts' : 'bin',
    isWin ? 'gunicorn.exe' : 'gunicorn',
  );
  if (fs.existsSync(candidate)) return candidate;

  throw new Error(
    'Could not find Gunicorn in backend/.venv.\n' +
    'Create it and install dependencies with:\n' +
    'cd backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt'
  );
}

module.exports = {
  apps: [
    {
      // ── Frontend: Next.js custom server ──────────────────────────
      name: 'yaqeen-frontend',
      cwd: './frontend',
      script: 'server.mjs',
      env: {
        NODE_ENV: 'production',
        PORT: PORT,
        HOST: HOST,
      },
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '../logs/frontend-error.log',
      out_file: '../logs/frontend-out.log',
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      // Uncomment for HTTPS:
      // env: {
      //   NODE_ENV: 'production',
      //   PORT: PORT,
      //   HOST: HOST,
      //   USE_HTTPS: 'true',
      // },
    },
    {
      // ── Backend: Django WSGI via Gunicorn in backend/.venv ──────
      name: 'yaqeen-backend',
      cwd: './backend',
      script: findGunicorn(),
      args: `config.wsgi:application --bind ${BACKEND_HOST}:${BACKEND_PORT} --workers 3 --timeout 120`,
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      error_file: '../logs/backend-error.log',
      out_file: '../logs/backend-out.log',
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    },
  ],
};
