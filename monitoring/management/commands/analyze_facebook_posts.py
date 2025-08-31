# This management commands will analyze all media posts in the database using the model endpoints
# and print/save the results. This is a good place for batch or scheduled analysis.

from django.core.management.base import BaseCommand
from monitoring.models import FacebookPost  # In future, replace with a generic MediaPost model
from monitoring.model_client import analyze_hate, analyze_misinformation

class Command(BaseCommand):
    help = 'Analyze media posts for hate and misinformation using the model endpoints.'

    def handle(self, *args, **options):
        posts = FacebookPost.objects.all()  # Replace with MediaPost.objects.all() when available
        self.stdout.write(f"Analyzing {posts.count()} media posts...")
        for post in posts:
            content = post.text or ''
            if not content.strip():
                continue
            hate_result = analyze_hate(content)
            misinformation_result = analyze_misinformation(content)
            self.stdout.write(f"Post ID: {post.post_id}")
            self.stdout.write(f"  Hate Analysis: {hate_result}")
            self.stdout.write(f"  Misinformation Analysis: {misinformation_result}")
            # Optionally, save results to the database or take further action here
        self.stdout.write(self.style.SUCCESS('Analysis complete.'))
