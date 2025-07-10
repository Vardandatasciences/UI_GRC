const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    },
    hot: false,            // Disable Hot Module Replacement (HMR)
    liveReload: false,     // Disable live reload
    client: {
      overlay: false       // Prevent fullscreen error overlay
    },
    host: '0.0.0.0',        // Required for GitHub Codespaces
    port: 8080             // Match Codespaces port
  }
});
