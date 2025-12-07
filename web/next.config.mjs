/** @type {import('next').NextConfig} */
const nextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://advent.muza.team/api/:path*", // Проксируем API запросы на бэкенд (HTTPS)
        // Не добавляем trailing slash автоматически
      },
    ];
  },
  // Отключаем автоматическое добавление trailing slash
  trailingSlash: false,
};

export default nextConfig;
