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
    visibleUsers(state) {
      if (!state.user) return [];
      if (this.isAdmin) {
        return state.users;
      } else {
        return state.users.filter(user => user.id === state.user?.id);
      }
    }
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const response = await axios.post(`${useRuntimeConfig().public.apiBase}/login/`, { 
          username, 
          password 
        });
        
        this.token = response.data.access;
        localStorage.setItem('token', this.token);
        this.user = response.data.user;
        
        if (this.isAdmin) {
          await this.fetchAllUsers();
        } else {
          this.users = [this.user];
        }
        
        console.log('Login realizado com sucesso');
        return true;
      } catch (error) {
        console.error('Erro no login:', error);
        throw new Error('Credenciais inválidas');
      }
    },

    async registerClient(username: string, email: string, password: string) {
      try {
        await axios.post(`${useRuntimeConfig().public.apiBase}/api/register/client/`, { 
          username, 
          email, 
          password 
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
    }) {
      try {
        await axios.post(`${useRuntimeConfig().public.apiBase}/api/register/store/`, storeData);
      } catch (error) {
        console.error('Erro ao registrar loja:', error);
        throw new Error('Erro no registro da loja');
      }
    },

    async fetchAllUsers() {
      if (!this.token) throw new Error('Não autenticado');
      if (!this.isAdmin) throw new Error('Acesso não autorizado');

      try {
        const response = await axios.get(`${useRuntimeConfig().public.apiBase}/users/`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.users = response.data;
        console.log('Usuários carregados:', this.users);
      } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        throw new Error('Falha ao carregar usuários');
      }
    },

    async fetchCurrentUser() {
      if (!this.token || !this.user) throw new Error('Não autenticado');

      try {
        let endpoint = '';
        if (this.isStore) {
          endpoint = '/api/store/profile/';
        } else {
          endpoint = `/users/${this.user.id}/`;
        }

        const response = await axios.get(
          `${useRuntimeConfig().public.apiBase}${endpoint}`,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        this.user = response.data;
        this.users = this.isAdmin ? this.users : [this.user];
        return this.user;
      } catch (error) {
        console.error('Erro ao buscar perfil:', error);
        throw error;
      }
    },

    async updateStoreProfile(profileData: {
      email?: string;
      cnpj?: string;
      address?: string;
      responsible?: string;
      latitude?: number;
      longitude?: number;
    }) {
      if (!this.token || !this.isStore) throw new Error('Não autorizado');

      try {
        const response = await axios.put(
          `${useRuntimeConfig().public.apiBase}/api/store/profile/`,
          profileData,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        
        this.user = response.data;
        this.users = this.isAdmin ? this.users.map(u => u.id === this.user.id ? this.user : u) : [this.user];
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
    }) {
      if (!this.token || !this.isAdmin) throw new Error('Não autorizado');

      try {
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
        }
        
        console.log('Usuário atualizado:', response.data);
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
        console.log('Usuário excluído:', userId);
      } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        throw new Error('Falha ao excluir usuário');
      }
    },

    async deleteAccount() {
      if (!this.token || !this.user) throw new Error('Não autenticado');

      try {
        let endpoint = '';
        if (this.isStore) {
          endpoint = '/api/store/profile/';
        } else {
          endpoint = `/users/${this.user.id}/`;
        }

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
    },

    async initialize() {
      const token = localStorage.getItem('token');
      if (token) {
        this.token = token;
        try {
          await this.fetchCurrentUser();
          if (this.isAdmin) {
            await this.fetchAllUsers();
          }
        } catch (error) {
          this.logout();
        }
      }
    }
  },

  persist: {
    paths: ['user', 'token'],
    afterRestore: (context) => {
      const store = useAuthStore();
      store.initialize();
    }
  }
});