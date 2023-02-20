<script>
import axios from "axios";

const csrfToken = document.cookie["csrftoken"];
const formTypes = {
    CHECKBOX: "CHECKBOX",
    RADIO: "RADIO",
};

axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

export default {
    name: "Question",
    data() {
        return {
            question: {},
            choices: [],
            formType: formTypes.RADIO,
            selectedOptions: [],
            answerChoices: [],
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
                    this.question = data;
                    this.choices = data["choices"];
                    this.formType = this.question.is_multichoice
                        ? formTypes.CHECKBOX
                        : formTypes.RADIO;
                })
                .catch((error) => {
                    console.error(
                        "There was a problem with the fetchQuestionData operation:",
                        error
                    );
                });
        },

        async fetchChoiceData(uuid) {
            try {
                const response = await axios.get(`/api/choices/${uuid}/`);
                return response.data;
            } catch (error) {
                console.error(error);
                throw error;
            }
        },
        async checkRadioForm() {
            const answer = this.choices.find((choice) => {
                return choice.text === this.selectedOptions;
            });
            const choiceUUID = answer.uuid.toString();
            const choiceData = await this.fetchChoiceData(choiceUUID);
            this.answerChoices.push(choiceUUID);
            this.answerResult = choiceData.is_correct;
        },

        async checkCheckboxForm() {
            let allCorrect = true;
            for (const selectedOption of this.selectedOptions) {
                const answer = this.choices.find(
                    (choice) => choice.text === selectedOption
                );
                const choiceUUID = answer.uuid.toString();
                const choiceData = await this.fetchChoiceData(choiceUUID);
                this.answerChoices.push(choiceUUID);

                if (!choiceData.is_correct) {
                    allCorrect = false;
                }
            }
            this.answerResult = allCorrect;
        },

        async checkAnswers() {
            if (this.formType === formTypes.RADIO) {
                await this.checkRadioForm();
            } else if (this.formType === formTypes.CHECKBOX) {
                await this.checkCheckboxForm(this);
            }
        },

        async saveUserAnswer() {
            const postData = {
                question: this.question.uuid,
                choices: this.answerChoices.map((choice) => ({ uuid: choice })),
                is_correct: this.answerResult,
            };
            try {
                const response = await axios.post("/api/answers/", postData);
                console.log(response.data);
            } catch (error) {
                console.error(
                    "There was a problem with the saveUserAnswer operation:",
                    error
                );
            }
        },

        async submitForm() {
            if (!this.selectedOptions.length || this.formSubmitted) {
                return;
            }
            await this.checkAnswers();
            this.saveUserAnswer();
            this.formSubmitted = true;
        },
    },
};
</script>

<template>
    <h1>{{ question.title }}</h1>

    <template v-if="formType === 'RADIO'">
        <form @submit.prevent="submitForm">
            <p v-for="(choice, index) in choices" :key="choice.uuid">
                <input :id="'option' + (index + 1)" type="radio" :value="choice.text" v-model="selectedOptions"
                    name="question" />
                <label :for="'option' + (index + 1)">{{ choice.text }} {{ choice.is_correct }}</label>
            </p>
            <button type="submit" :disabled="formSubmitted">Submit</button>
        </form>
    </template>
    <template v-else>
        <form @submit.prevent="submitForm">
            <p v-for="(choice, index) in choices" :key="choice.uuid">
                <input :id="'option' + (index + 1)" type="checkbox" :value="choice.text" v-model="selectedOptions"
                    name="question" />
                <label :for="'option' + (index + 1)">{{ choice.text }} {{ choice.is_correct }}</label>
            </p>
            <button type="submit" :disabled="formSubmitted">Submit</button>
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
