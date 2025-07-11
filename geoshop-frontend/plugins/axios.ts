import axios from 'axios';

export default defineNuxtPlugin((nuxtApp) => {
  axios.defaults.baseURL = useRuntimeConfig().public.apiBase;
  return {
    provide: {
      axios,
    },
  };
});