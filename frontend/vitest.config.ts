import { fileURLToPath, URL } from "node:url";
import { createRequire } from "node:module";
import { defineConfig } from "vitest/config";

const require = createRequire(import.meta.url);
const vuePlugin = require("@vitejs/plugin-vue").default;

export default defineConfig({
  plugins: [vuePlugin()],
  test: {
    environment: "happy-dom",
    globals: true,
    include: ["src/**/*.spec.ts"]
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  }
});
