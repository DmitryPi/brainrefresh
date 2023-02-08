<script setup>
import { RouterLink, RouterView } from "vue-router";
import Question from "./components/Question.vue";
import QuestionList from "./components/QuestionList.vue";
</script>

<template>
    <header>
        <nav>
            <RouterLink :to="{ name: 'home' }">Home</RouterLink>
            <RouterLink :to="{ name: 'about' }">About</RouterLink>
        </nav>
    </header>

    <RouterView />
</template>

<style scoped>
</style>
