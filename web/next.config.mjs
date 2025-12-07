/** @type {import('next').NextConfig} */
const nextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://advent.muza.team/api/:path*", // Проксируем API запросы на бэкенд
      },
    ];
  },
};

export default nextConfig;
