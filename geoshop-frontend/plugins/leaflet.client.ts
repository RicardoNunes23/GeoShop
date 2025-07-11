import { defineNuxtPlugin } from '#app'

export default defineNuxtPlugin(() => {
  // Apenas no lado do cliente
  if (process.client) {
    return {
      provide: {
        leaflet: () => import('leaflet')
      }
    }
  }
})