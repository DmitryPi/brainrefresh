<script>
const formTypes = {
    CHECKBOX: "CHECKBOX",
    RADIO: "RADIO",
};

export default {
    name: "Question",
    data() {
        return {
            question: {},
            choices: [],
            formType: formTypes.RADIO,
            selectedOptions: [],
            answerResult: null,
            formSubmitted: false,
            questionExplain: false,
        };
    },
    created() {
        this.fetchQuestionData(this.$route.params.uuid);
    },
    methods: {
        fetchQuestionData(uuid) {
            fetch(`/api/questions/${uuid}/`, {
                cache: "no-cache",
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log(data);
                    this.question = data;
                    this.choices = data["choices"];
                })
                .catch((error) => {
                    console.error(
                        "There was a problem with the fetch operation:",
                        error
                    );
                });
        },

        setFormType() {
            const correctChoices = this.choices.filter(
                (choice) => choice.is_correct === true
            );
            this.formType =
                correctChoices.length > 1
                    ? formTypes.CHECKBOX
                    : formTypes.RADIO;
        },

        checkRadio() {
            const answer = this.choices.find((choice) => {
                return choice.text === this.selectedOptions;
            });
            this.answerResult = answer.is_correct;
        },

        checkCheckbox() {
            let allCorrect = true;
            this.selectedOptions.forEach((selectedOption) => {
                const answer = this.choices.find(
                    (choice) => choice.text === selectedOption
                );
                if (!answer || !answer.is_correct) {
                    allCorrect = false;
                }
            });
            this.answerResult = allCorrect;
        },

        checkAnswers() {
            switch (this.formType) {
                case formTypes.RADIO:
                    this.checkRadio();
                    break;
                case formTypes.CHECKBOX:
                    this.checkCheckbox(this);
                    break;
            }
        },

        saveAnswer() {},

        submitForm() {
            if (!this.selectedOptions.length) {
                return;
            }
            this.formSubmitted = true;
            this.checkAnswers();
            this.saveAnswer();
        },
    },
};
</script>

<template>
    <h1>{{ question.title }}</h1>

    <template v-if="formType === 'RADIO'">
        <form @submit.prevent="submitForm">
            <p v-for="(choice, index) in choices" :key="choice.uuid">
                <input
                    :id="'option' + (index + 1)"
                    type="radio"
                    :value="choice.text"
                    v-model="selectedOptions"
                    name="question"
                />
                <label :for="'option' + (index + 1)">{{ choice.text }} {{ choice.is_correct }}</label>
            </p>
            <button type="submit">Submit</button>
        </form>
    </template>
    <template v-else>
        <form @submit.prevent="submitForm">
            <p v-for="(choice, index) in choices" :key="choice.uuid">
                <input
                    :id="'option' + (index + 1)"
                    type="checkbox"
                    :value="choice.text"
                    v-model="selectedOptions"
                    name="question"
                />
                <label :for="'option' + (index + 1)">{{ choice.text }} {{ choice.is_correct }}</label>
            </p>
            <button type="submit">Submit</button>
        </form>
    </template>

    <div v-if="formSubmitted">
        <p v-if="answerResult">Ответ верный</p>
        <p v-else>Ответ не верный</p>
        <div>
            <button @click="questionExplain = !questionExplain">Объяснение</button>
            <p v-if="questionExplain">{{ question.explanation }}</p>
        </div>
    </div>
</template>
