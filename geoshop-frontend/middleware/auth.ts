export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();
  const publicRoutes = ['/login', '/register'];

  if (publicRoutes.includes(to.path)) return;

  if (process.client && !auth.token) {
    const token = localStorage.getItem('token');
    if (token) auth.token = token;
  }

  if (!auth.token) {
    return navigateTo('/login');
  }

  if (!auth.user) {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        auth.user = JSON.parse(storedUser);
        if (auth.isAdmin) {
          await auth.fetchAllUsers();
        } else if (auth.isStore) {
          await auth.fetchProfile();
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

  if (auth.isStore && to.path.startsWith('/admin')) {
    return navigateTo('/store?view=profile');
  }

  if (auth.isStore && !to.path.startsWith('/store')) {
    return navigateTo('/store?view=profile');
  }

  if (auth.isAdmin && !to.path.startsWith('/admin')) {
    return navigateTo('/admin?view=profile');
  }

  return;
});