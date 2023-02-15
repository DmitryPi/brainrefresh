import axios from 'axios';
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null
    }),
    getters: {
        getUser(state) {
            return state.user
        }
    },
    actions: {
        async fetchUser() {
            try {
                const response = await axios.get('/api/users/me/');
                console.log(response.data);
                this.user = response.data;
            } catch (error) {
                console.error(error)
            }
        }
    }
})
