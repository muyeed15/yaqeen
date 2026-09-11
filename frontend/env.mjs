import { existsSync, readFileSync } from "fs";

export function loadEnv(filePath) {
  if (!existsSync(filePath)) {
    throw new Error(`Required environment file not found: ${filePath}`);
  }
  const env = {};
  for (const line of readFileSync(filePath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const separator = trimmed.indexOf("=");
    if (separator === -1) continue;
    const key = trimmed.slice(0, separator).trim();
    const value = trimmed.slice(separator + 1).trim();
    if (!(key in process.env)) process.env[key] = value;
    env[key] = process.env[key];
  }
  return env;
}

export function requiredEnv(env, name) {
  const value = env[name];
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${name} must be set in frontend/.env`);
  }
  return value.trim();
}
