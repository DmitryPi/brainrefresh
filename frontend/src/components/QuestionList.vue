
<script>
const API_URL = import.meta.env.VITE_API_HOST_URL;

export default {
    data() {
        return {
            loading: true,
            questions: [],
        };
    },
    mounted() {
        fetch(`${API_URL}/questions/`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                this.loading = false;
                this.questions = data;
            })
            .catch((error) => {
                console.error(
                    "There was a problem with the fetch operation:",
                    error
                );
            });
    },
};
</script>

<template>
    <div v-if="loading">Loading...</div>
    <ul v-else class="questions">
        <li
            class="questions__question"
            v-for="question in questions"
            :key="question.uuid"
        >
            <router-link
                :to="{ name: 'question', params: { uuid: question.uuid } }"
            >
                <span>{{ question.title }}</span>
                <p>{{ question.tags.label }}</p>
                <span>{{ question.created_at }}</span>
            </router-link>
        </li>
    </ul>
</template>

<style lang="scss" scoped>
.questions {
    display: flex;
    flex-direction: column;
}
.questions__question {
    padding: 0.5em 1em;
    margin-bottom: 1em;
    border: 1px solid var(--color-border);
    border-radius: 5px;
    &:hover {
        background-color: var(--color-background-soft);
        border: 1px solid var(--color-border-hover);
    }
    a {
        display: block;
        background: none;
    }
}
</style>
