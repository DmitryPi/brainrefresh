<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { onMounted, computed } from "vue";

const store = useAuthStore();
const user = computed(() => {
    return store.user;
});
onMounted(() => {
    store.fetchUser();
});
</script>


<template>
    <header>
        <nav>
            <RouterLink :to="{ name: 'home' }">Home</RouterLink>
            <RouterLink :to="{ name: 'about' }">About</RouterLink>
            <div v-if="user">Welcome, {{ user.username }}!</div>
            <div v-else>Please log in.</div>
        </nav>
    </header>

    <RouterView />
</template>

<style lang="scss" scoped>
</style>
