<script>
import moment from "moment";

const PAGINATION_LIMIT = 10;

export default {
    name: "QuestionList",
    data() {
        return {
            loading: true,
            questions: [],
        };
    },
    mounted() {
        fetch(`/api/questions/?limit=${PAGINATION_LIMIT}`, {
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
                this.loading = false;
                this.questions = data["results"];
            })
            .catch((error) => {
                console.error(
                    "There was a problem with the fetch operation:",
                    error
                );
            });
    },
    methods: {
        formatDate(date) {
            const DATE_FMT = "MMMM Do YYYY, h:mm:ss";
            return moment(date).format(DATE_FMT);
        },
    },
};
</script>

<template>
    <div v-if="loading">Loading...</div>
    <ul v-else class="questions">
        <li class="questions__question" v-for="question in questions" :key="question.uuid">
            <router-link
                :to="{ name: 'question', params: { uuid: question.uuid } }"
                class="question-card"
            >
                <h3 class="question-card--title">{{ question.title }}</h3>
                <div class="question-card__tags">
                    <router-link
                        :to="{ name: 'tag', params: { slug: tag.slug } }"
                        v-for="tag in question.tags"
                        :key="tag.slug"
                        class="tag-badge"
                    >{{ tag.label }}</router-link>
                </div>
                <span>Created: {{ formatDate(question.created_at) }}</span>
            </router-link>
        </li>
    </ul>
</template>

<style lang="scss" scoped>
.questions {
    display: flex;
    flex-direction: column;
    .question-card {
        display: block;
        padding: 0.5em 1em;
        margin-bottom: 1em;
        border: 1px solid var(--color-border);
        border-radius: 5px;
        &:hover {
            background-color: var(--color-background-soft);
            border: 1px solid var(--color-border-hover);
        }
        &--title {
            font-size: 1.3rem;
            font-weight: bold;
        }
        &__tags {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 3px;
            margin: 5px 0px;
            font-size: 0.8rem;
            .tag-badge {
                background-color: black;
                color: white;
                border-radius: 20px;
                padding: 3px 8px;
                &:hover {
                    background-color: red;
                    color: white;
                }
            }
        }
    }
}
</style>
