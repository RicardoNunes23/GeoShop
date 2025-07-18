import { mask } from 'vue-the-mask'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('mask', mask)
  
  // Para TypeScript, você pode adicionar a tipagem da diretiva
  return {
    provide: {
      mask: mask
    }
  }
})