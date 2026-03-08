import log from "loglevel";

export type LoggerContext = Record<string, unknown>;

const root = log.getLogger("chatweb");
root.setDefaultLevel("debug");

function withContext(message: string, context?: LoggerContext): string {
  if (!context) return message;
  return `${message} ${JSON.stringify(context)}`;
}

export const logger = {
  debug(message: string, context?: LoggerContext) {
    root.debug(withContext(message, context));
  },
  info(message: string, context?: LoggerContext) {
    root.info(withContext(message, context));
  },
  warn(message: string, context?: LoggerContext) {
    root.warn(withContext(message, context));
  },
  error(message: string, context?: LoggerContext) {
    root.error(withContext(message, context));
  }
};
