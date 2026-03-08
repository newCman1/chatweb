import { fileURLToPath, URL } from "node:url";
import { createRequire } from "node:module";
import { defineConfig } from "vite";

const require = createRequire(import.meta.url);
const vuePlugin = require("@vitejs/plugin-vue").default;

export default defineConfig({
  plugins: [vuePlugin()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url))
    }
  }
});
