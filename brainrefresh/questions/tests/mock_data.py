import random

from .factories import ChoiceFactory, Question, Tag, TagFactory

tag_names = [
    "Python",
    "Django",
    "Flask",
    "REST",
    "API",
    "React",
    "JavaScript",
    "Node.js",
    "Vue.js",
    "Angular",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "Google Cloud",
    "Heroku",
    "DevOps",
    "CI/CD",
    "Git",
    "GitHub",
    "Bitbucket",
    "Agile",
    "Scrum",
    "Kanban",
    "CSS",
    "Sass",
    "Bootstrap",
    "Materialize",
    "JQuery",
    "Web Development",
    "Mobile Development",
    "Machine Learning",
    "Data Science",
    "Artificial Intelligence",
    "Natural Language Processing",
    "Computer Vision",
    "Deep Learning",
]


def create_tags() -> list[Tag]:
    tags = []
    for tag_name in tag_names:
        tag = TagFactory(label=tag_name)
        tags.append(tag)
    return tags


def delete_tags() -> None:
    tags = Tag.objects.all()
    for tag in tags:
        tag.delete()


def add_random_tags_to_questions() -> None:
    questions = Question.objects.all()
    tags = Tag.objects.all()

    for question in questions:
        random_tags = [random.choice(tags) for _ in range(random.randint(1, 5))]
        question.tags.set(random_tags)


def add_choices_to_questions() -> None:
    questions = Question.objects.all()
    for question in questions:
        batch_size = random.randint(1, 3)
        ChoiceFactory.create_batch(batch_size, question=question)
