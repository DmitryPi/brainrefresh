import axios from 'axios';
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null
    }),
    getters: {
        getUser(state) {
            return state.user;
        }
    },
    actions: {
        async fetchUser() {
            try {
                const response = await axios.get('/api/users/me/');
                this.user = response.data;
            } catch (error) {
                if (error.code === "ERR_BAD_REQUEST") {
                    console.log("Not authenticated: 403");
                } else {
                    console.error(error);
                }
            }
        }
    }
});
