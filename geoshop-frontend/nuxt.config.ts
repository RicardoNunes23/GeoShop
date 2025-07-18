export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: [
    '@pinia/nuxt',
    '@nuxt/eslint',
  ],
  css: [
    '~/assets/css/main.css',
    'vuetify/styles',
    '@mdi/font/css/materialdesignicons.min.css',
    'leaflet/dist/leaflet.css',
  ],
  plugins: ['~/plugins/vuetify.ts', '~/plugins/mask.ts'],
  build: {
    transpile: ['vuetify', 'vue3-leaflet', 'leaflet'],
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api',
    },
  },
  vite: {
    define: {
      'process.env.DEBUG': 'false',
    },
    optimizeDeps: {
      include: ['leaflet', 'object-assign'],
    },
    resolve: {
      alias: {
        'object-assign': 'object-assign', // Força o uso do módulo correto
      },
    },
  },
  routeRules: {
    '/**': { middleware: ['auth'] },
    '/login': { middleware: [] },
    '/register': { middleware: [] },
  },
});