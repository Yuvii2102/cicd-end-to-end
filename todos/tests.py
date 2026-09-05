from django.test import TestCase

from .models import Todo


class TodoModelTest(TestCase):

    def test_todo_creation(self):
        todo = Todo.objects.create(
            title="Learn CI/CD"
        )

        self.assertEqual(todo.title, "Learn CI/CD")
