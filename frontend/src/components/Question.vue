<script>
const API_URL = import.meta.env.VITE_API_HOST_URL;

export default {
    name: "Question",
    data() {
        return {
            question: {},
            choices: [],
            selectedOption: "",
            selectedOptionResult: null,
            formSubmitted: false,
            questionExplain: false,
        };
    },
    created() {
        this.fetchQuestionData(this.$route.params.uuid);
        this.fetchQuestionChoices(this.$route.params.uuid);
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
        fetchQuestionChoices(uuid) {
            fetch(`${API_URL}/questions/${uuid}/choices/`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    this.choices = data;
                })
                .catch((error) => {
                    console.error(
                        "There was a problem with the fetch operation:",
                        error
                    );
                });
        },
        checkAnswer() {
            const answer = this.choices.find((choice) => {
                return choice.text === this.selectedOption;
            });
            this.selectedOptionResult = answer.is_correct;
        },
        saveAnswer() {},
        submitForm() {
            this.formSubmitted = true;
            this.checkAnswer();
        },
    },
};
</script>

<template>
    <h1>{{ question.title }}</h1>
    <form @submit.prevent="submitForm">
        <p v-for="(choice, index) in choices" :key="choice.uuid">
            <input
                :id="'option' + (index + 1)"
                type="radio"
                :value="choice.text"
                v-model="selectedOption"
                name="question"
            />
            <label :for="'option' + (index + 1)"
                >{{ choice.text }} {{ choice.is_correct }}</label
            >
        </p>
        <button type="submit">Submit</button>
    </form>
    <div v-if="formSubmitted">
        <p v-if="selectedOptionResult">Ответ верный</p>
        <p v-else>Ответ не верный</p>
        <div>
            <button @click="questionExplain = !questionExplain">
                Объяснение
            </button>
            <p v-if="questionExplain">{{ question.explanation }}</p>
        </div>
    </div>
</template>
