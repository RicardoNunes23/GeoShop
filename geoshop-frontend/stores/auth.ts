import { defineStore } from 'pinia';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
  user_type: string;
  cnpj?: string;
  address?: string;
  responsible?: string;
  latitude?: number;
  longitude?: number;
  use_bulk_pricing?: boolean; // Novo campo
  has_loyalty_card?: boolean; // Novo campo
}

interface AuthState {
  user: User | null;
  token: string | null;
  users: User[];
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    users: [],
  }),

  getters: {
    isAdmin: (state) => state.user?.user_type === 'admin',
    isStore: (state) => state.user?.user_type === 'store',
    isClient: (state) => state.user?.user_type === 'client',
    isAuthenticated: (state) => !!state.token,
    visibleUsers(state) {
      if (!state.user) return [];
      return this.isAdmin ? state.users : state.users.filter(user => user.id === state.user?.id);
    },
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const response = await axios.post(`${useRuntimeConfig().public.apiBase}/login/`, {
          username,
          password,
        });

        this.token = response.data.access;
        this.user = response.data.user;
        localStorage.setItem('token', this.token);
        localStorage.setItem('user', JSON.stringify(this.user));

        if (this.isAdmin) {
          await this.fetchAllUsers();
        } else if (this.isStore) {
          await this.fetchProfile();
        } else {
          this.users = [this.user];
        }

        return true;
      } catch (error) {
        console.error('Erro no login:', error);
        throw new Error('Credenciais inválidas');
      }
    },

    async fetchProfile() {
      if (!this.token || !this.isStore) throw new Error('Não autorizado');

      try {
        const response = await axios.get(
          `${useRuntimeConfig().public.apiBase}/store/profile/`,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.user = { ...this.user, ...response.data };
        this.users = [this.user];
        localStorage.setItem('user', JSON.stringify(this.user));
        return this.user;
      } catch (error) {
        console.error('Erro ao buscar perfil:', error);
        throw error;
      }
    },

    async fetchAllUsers() {
      if (!this.isAdmin) throw new Error('Acesso não autorizado');

      try {
        const response = await axios.get(`${useRuntimeConfig().public.apiBase}/users/`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.users = response.data;
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        throw error;
      }
    },

    async registerClient(username: string, email: string, password: string) {
      try {
        await axios.post(`${useRuntimeConfig().public.apiBase}/register/client/`, {
          username,
          email,
          password,
        });
      } catch (error) {
        console.error('Erro ao registrar cliente:', error);
        throw new Error('Erro no registro do cliente');
      }
    },

    async registerStore(storeData: {
      username: string;
      email: string;
      password: string;
      cnpj: string;
      address: string;
      responsible: string;
      latitude: number;
      longitude: number;
      use_bulk_pricing: boolean;
      has_loyalty_card: boolean;
    }) {
      try {
        const response = await axios.post(`${useRuntimeConfig().public.apiBase}/register/store/`, {
          ...storeData,
          latitude: Number(storeData.latitude),
          longitude: Number(storeData.longitude),
        });
        
        return response.data;
      } catch (error: any) {
        console.error('Erro ao registrar loja:', error);
        throw new Error(error.response?.data?.message || 'Erro no registro da loja');
      }
    },

    async updateProfile(profileData: {
      email?: string;
      cnpj?: string;
      address?: string;
      responsible?: string;
      latitude?: number;
      longitude?: number;
      use_bulk_pricing?: boolean;
      has_loyalty_card?: boolean;
    }) {
      if (!this.token || !this.isStore) throw new Error('Não autorizado');

      try {
        // Garante que os campos numéricos sejam números
        if (profileData.latitude) profileData.latitude = Number(profileData.latitude);
        if (profileData.longitude) profileData.longitude = Number(profileData.longitude);

        const response = await axios.put(
          `${useRuntimeConfig().public.apiBase}/store/profile/`,
          profileData,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.user = { ...this.user, ...response.data };
        this.users = [this.user];
        localStorage.setItem('user', JSON.stringify(this.user));
        return this.user;
      } catch (error) {
        console.error('Erro ao atualizar perfil:', error);
        throw error;
      }
    },

    async updateUser(userData: {
      id: number;
      username: string;
      email: string;
      user_type: string;
      cnpj?: string;
      address?: string;
      responsible?: string;
      use_bulk_pricing?: boolean;
      has_loyalty_card?: boolean;
    }) {
      if (!this.token || !this.isAdmin) throw new Error('Não autorizado');

      try {
        // Para usuários que não são lojas, remove os campos específicos
        if (userData.user_type !== 'store') {
          delete userData.use_bulk_pricing;
          delete userData.has_loyalty_card;
        }

        const response = await axios.put(
          `${useRuntimeConfig().public.apiBase}/users/${userData.id}/`,
          userData,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.users = this.users.map(user =>
          user.id === userData.id ? response.data : user
        );

        if (this.user?.id === userData.id) {
          this.user = response.data;
          localStorage.setItem('user', JSON.stringify(this.user));
        }

        return response.data;
      } catch (error) {
        console.error('Erro ao atualizar usuário:', error);
        throw new Error('Falha ao atualizar usuário');
      }
    },

    async deleteUser(userId: number) {
      if (!this.token || !this.isAdmin) throw new Error('Não autorizado');
      if (this.user?.id === userId) throw new Error('Não é possível excluir a própria conta');

      try {
        await axios.delete(
          `${useRuntimeConfig().public.apiBase}/users/${userId}/`,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.users = this.users.filter(user => user.id !== userId);
      } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        throw new Error('Falha ao excluir usuário');
      }
    },

    async deleteProfile() {
      if (!this.token || !this.user) throw new Error('Não autenticado');

      try {
        const endpoint = this.isStore ? '/store/profile/' : `/users/${this.user.id}/`;
        await axios.delete(
          `${useRuntimeConfig().public.apiBase}${endpoint}`,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.logout();
      } catch (error) {
        console.error('Erro ao excluir conta:', error);
        throw error;
      }
    },

    logout() {
      this.user = null;
      this.token = null;
      this.users = [];
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },

    async initialize() {
      const token = localStorage.getItem('token');
      if (token) {
        this.token = token;
        try {
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            this.user = JSON.parse(storedUser);
            if (this.isAdmin) {
              await this.fetchAllUsers();
            } else if (this.isStore) {
              await this.fetchProfile();
            } else {
              this.users = [this.user];
            }
          }
        } catch (error) {
          this.logout();
        }
      }
    },
  },

  persist: {
    paths: ['user', 'token'],
    afterRestore: (context) => {
      const store = useAuthStore();
      store.initialize();
    },
  },
});