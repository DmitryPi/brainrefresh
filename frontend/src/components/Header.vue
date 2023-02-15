How to get props user in my data and should i even do that?

<script>
export default {
    name: "Header",
    props: {
        user: {
            type: Object,
            default: null,
        },
    },
};
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
</template>

<style lang="scss" scoped>
</style>
