/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Emit a self-contained production server (.next/standalone) so the Docker
  // image can run `node server.js` with only the traced dependencies instead
  // of copying the entire node_modules tree. No effect on `next dev` or the
  // ordinary `next start`, so local development is unchanged.
  output: "standalone",
};

module.exports = nextConfig;
