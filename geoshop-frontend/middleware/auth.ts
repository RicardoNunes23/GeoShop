import { defineNuxtRouteMiddleware, navigateTo } from '#app';
import { useAuthStore } from '~/stores/auth';

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore();

  // Verifica se estamos no lado do cliente
  const isClient = process.client;

  // Verifica se o usuário está autenticado (tem token e user no store)
  if (!authStore.token || !authStore.user) {
    if (isClient) {
      // No lado do cliente, tenta recuperar o token do localStorage
      const token = localStorage.getItem('token');
      if (token) {
        console.log('Token encontrado no localStorage:', token);
        // Tenta buscar os dados do usuário
        return authStore.fetchStoreProfile().catch((error) => {
          console.error('Falha ao buscar perfil:', error);
          return navigateTo('/login');
        });
      } else {
        console.log('Nenhum token encontrado no localStorage, redirecionando para /login');
        return navigateTo('/login');
      }
    } else {
      // No lado do servidor, redireciona para /login se não houver token
      console.log('Executando no servidor, nenhum token disponível, redirecionando para /login');
      return navigateTo('/login');
    }
  }

  // Se o usuário está autenticado, permite o acesso à rota
  console.log('Usuário autenticado, permitindo acesso à rota:', to.path);
  return;
});