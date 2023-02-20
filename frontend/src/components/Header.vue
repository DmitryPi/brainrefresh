<script setup>
import { useAuthStore } from "@/stores/auth";
import { computed } from "vue";

const store = useAuthStore();
const user = computed(() => {
    return store.user;
});

</script>

<template>
    <header>
        <nav>
            <RouterLink :to="{ name: 'home' }">Home</RouterLink>
            <RouterLink :to="{ name: 'about' }">About</RouterLink>
        </nav>
        <div v-if="user">Welcome, {{ user.username }}!</div>
        <div v-else>Please log in.</div>
    </header>
</template>

<style lang="scss" scoped>
header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

nav {
    display: flex;
    gap: 0.5rem
}
</style>
