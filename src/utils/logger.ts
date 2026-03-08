import log from "loglevel";

export type LoggerContext = Record<string, unknown>;
type FrontendLogLevel = "debug" | "info" | "warn" | "warning" | "error";

const SENSITIVE_KEYS = new Set(["authorization", "token", "password", "secret", "apiKey", "api_key"]);

const root = log.getLogger("chatweb");
const envLevel = (import.meta.env.VITE_LOG_LEVEL ?? "debug").toLowerCase() as FrontendLogLevel;
root.setDefaultLevel(envLevel === "warning" ? "warn" : envLevel);

function redact(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => redact(item));
  }
  if (value && typeof value === "object") {
    const input = value as Record<string, unknown>;
    const output: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(input)) {
      output[key] = SENSITIVE_KEYS.has(key) ? "***" : redact(val);
    }
    return output;
  }
  return value;
}

function withContext(message: string, context?: LoggerContext): string {
  if (!context) return message;
  return `${message} ${JSON.stringify(redact(context))}`;
}

export const logger = {
  debug(message: string, context?: LoggerContext) {
    root.debug(withContext(message, context));
  },
  info(message: string, context?: LoggerContext) {
    root.info(withContext(message, context));
  },
  warning(message: string, context?: LoggerContext) {
    root.warn(withContext(message, context));
  },
  warn(message: string, context?: LoggerContext) {
    root.warn(withContext(message, context));
  },
  error(message: string, context?: LoggerContext) {
    root.error(withContext(message, context));
  }
};
