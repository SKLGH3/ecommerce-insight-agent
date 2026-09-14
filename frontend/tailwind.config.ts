/**
 * Tailwind CSS 主题配置
 * 定义前端项目的字体、颜色和阴影扩展
 */
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '"LXGW WenKai Screen"',
          '"Noto Sans SC"',
          '"PingFang SC"',
          '"Microsoft YaHei"',
          "sans-serif",
        ],
        mono: ['"JetBrains Mono"', '"SFMono-Regular"', "Consolas", "monospace"],
      },
      colors: {
        cloud: "#f3f7fb",
        slate: "#13233f",
        midnight: "#07172e",
        brand: "#f97316",
        accent: "#2563eb",
        danger: "#dc2626",
        mist: "#d9e5f4",
      },
      boxShadow: {
        line: "0 1px 0 rgba(19, 35, 63, 0.09)",
        panel: "0 24px 70px rgba(7, 23, 46, 0.15)",
      },
    },
  },
  plugins: [],
} satisfies Config;
