<script setup>
import { useAuthStore } from "@/stores/auth";
import { onMounted } from "vue";
import Header from "./components/Header.vue";

const store = useAuthStore();
onMounted(() => {
    store.fetchUser();
});
</script>


<template>
    <Header />
    <RouterView />
</template>
