<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Question from "./components/Question.vue";
import QuestionList from "./components/QuestionList.vue";
</script>

<template>
    <header>
        <nav>
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/about">About</RouterLink>
        </nav>
    </header>

    <RouterView />
</template>

<style scoped>
</style>
