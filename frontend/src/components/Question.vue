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
        fetch(`${API_URL}/questions/f6f2bec8-6782-4c7c-8735-6f2010597dfc/`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                console.log(data);
                this.loading = false;
                this.question = data;
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
    <div class="question">{{ question.uuid }}</div>
</template>
