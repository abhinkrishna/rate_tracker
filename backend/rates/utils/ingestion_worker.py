from django.contrib.auth import get_user_model

User = get_user_model()


class IngestionWorker:
    @staticmethod
    def test():
        # 1. Simulate heavy work
        total = 0
        for i in range(10_000_000):
            total += i

        # 2. DB access (test Django ORM inside Celery)
        user_count = User.objects.count()

        return {
            "status": "success",
            "sum": total,
            "user_count": user_count,
        }
