<script setup>
import { useAuthStore } from "@/stores/auth";
import Header from "./components/Header.vue";
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
    <Header :user="user" />
    <RouterView />
</template>
