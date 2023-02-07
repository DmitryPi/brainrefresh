<script>
const API_URL = import.meta.env.VITE_API_HOST_URL;

export default {
    name: "Question",
    data() {
        return {
            question: {},
        };
    },
    created() {
        this.fetchQuestionData(this.$route.params.uuid);
    },
    methods: {
        fetchQuestionData(uuid) {
            fetch(`${API_URL}/questions/${uuid}/`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    this.question = data;
                })
                .catch((error) => {
                    console.error(
                        "There was a problem with the fetch operation:",
                        error
                    );
                });
        },
    },
};
</script>

<template>
    <div class="question">{{ question.uuid }}</div>
</template>
