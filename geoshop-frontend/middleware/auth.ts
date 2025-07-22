export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();
  const publicRoutes = ['/login', '/register'];

  // Rotas públicas não requerem autenticação
  if (publicRoutes.includes(to.path)) return;

  // Tenta recuperar o token do localStorage no client-side
  if (process.client && !auth.token) {
    const token = localStorage.getItem('token');
    if (token) auth.token = token;
  }

  // Redireciona se não tiver token
  if (!auth.token) {
    return navigateTo('/login');
  }

  // Carrega os dados do usuário se não estiverem carregados
  if (!auth.user) {
    try {
      const storedUser = localStorage.getItem('user');
      
      if (storedUser) {
        auth.user = JSON.parse(storedUser);
        
        // Carrega dados adicionais conforme o tipo de usuário
        if (auth.isAdmin) {
          await auth.fetchAllUsers();
        } else if (auth.isStore) {
          await auth.fetchProfile();
        } else if (auth.isClient) {
          // Adicione aqui qualquer fetch específico para clientes
          await auth.fetchClientProfile(); // Exemplo hipotético
        } else {
          auth.users = [auth.user];
        }
      } else {
        auth.logout();
        return navigateTo('/login');
      }
    } catch (error) {
      console.error('Falha ao carregar perfil:', error);
      auth.logout();
      return navigateTo('/login');
    }
  }

  // Regras de redirecionamento por tipo de usuário
  if (auth.isAdmin && !to.path.startsWith('/admin')) {
    return navigateTo('/admin?view=profile');
  }

  if (auth.isStore && !to.path.startsWith('/store')) {
    return navigateTo('/store?view=profile');
  }

  if (auth.isClient && !to.path.startsWith('/client')) {
    return navigateTo('/client?view=profile');
  }

  // Impede que usuários acessem áreas de outros tipos
  if (auth.isClient && (to.path.startsWith('/admin') || to.path.startsWith('/store'))) {
    return navigateTo('/client?view=profile');
  }

  if (auth.isStore && to.path.startsWith('/admin')) {
    return navigateTo('/store?view=profile');
  }

  if (auth.isAdmin && (to.path.startsWith('/store') || to.path.startsWith('/client'))) {
    return navigateTo('/admin?view=profile');
  }
});