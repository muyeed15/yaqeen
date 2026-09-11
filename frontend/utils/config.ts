const api = process.env.DJANGO_API_URL;
if (!api) throw new Error("DJANGO_API_URL must be set in frontend/.env");
export const API = api;
