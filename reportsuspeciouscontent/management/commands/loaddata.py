# your_app/management/commands/generate_mock_data.py
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from reportsuspeciouscontent.models import SuspiciousContentReport


class Command(BaseCommand):
    help = 'Generate and store mock data for SuspiciousContentReport model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Number of mock records to generate (default: 1000)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to spread the data across (default: 90)',
        )

    def handle(self, *args, **options):
        count = options['count']
        days = options['days']

        self.stdout.write(f'Generating {count} mock records...')


        cameroon_cities = [
            "Douala", "Yaoundé", "Bamenda", "Bafoussam", "Garoua",
            "Maroua", "Ngaoundéré", "Kumba", "Buea", "Limbe",
            "Edea", "Kousséri", "Nkongsamba", "Bertoua", "Ebolowa"
        ]

        reports = []

        for i in range(count):

            days_ago = random.randint(0, days)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            date_reported = timezone.now() - timedelta(
                days=days_ago, hours=hours_ago, minutes=minutes_ago
            )


            content_type_weights = [0.35, 0.25, 0.20, 0.15, 0.05]
            content_type = random.choices(
                ['hatespeech', 'misinformation', 'harassment', 'spam', 'fake'],
                weights=content_type_weights
            )[0]

            # Weighted urgency level based on content type
            if content_type in ['hatespeech', 'misinformation']:
                urgency_weights = [0.1, 0.2, 0.4, 0.3]  # More high/critical for serious content
            else:
                urgency_weights = [0.3, 0.4, 0.2, 0.1]  # More low/medium for less serious content

            urgency_level = random.choices(
                ['low', 'medium', 'high', 'critical'],
                weights=urgency_weights
            )[0]

            # Platform distribution
            platform_weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.04,
                                0.01]  # Facebook, Twitter, Instagram, YouTube, TikTok, WhatsApp, Other
            platform = random.choices(
                ['facebook', 'twitter', 'instagram', 'youtube', 'tiktok', 'whatsapp', 'other'],
                weights=platform_weights
            )[0]

            # Confidence score based on content type and urgency
            if content_type in ['hatespeech', 'misinformation'] and urgency_level in ['high', 'critical']:
                confidence_score = random.uniform(0.85, 0.99)
            else:
                confidence_score = random.uniform(0.6, 0.9)

            # Location - sometimes null
            location = random.choice(cameroon_cities) if random.random() < 0.8 else None

            # Generate realistic content based on type
            content = self.generate_content(content_type, urgency_level)

            # Create the report object
            report = SuspiciousContentReport(
                description=content,
                content_type=content_type,
                urgency_level=urgency_level,
                platform=platform,
                date_reported=date_reported,
                confidence_score=confidence_score,
                location=location,
                post_id=f"post_{random.randint(100000, 999999)}",
                user_id=f"user_{random.randint(1000, 9999)}"
            )

            reports.append(report)


            if len(reports) >= 100:
                SuspiciousContentReport.objects.bulk_create(reports)
                self.stdout.write(f'Created {len(reports)} records...')
                reports = []


        if reports:
            SuspiciousContentReport.objects.bulk_create(reports)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} mock records!')
        )

    def generate_content(self, content_type, urgency_level):
        """Generate realistic content based on type and urgency"""
        if content_type == "hatespeech":
            topics = ["Anglophones", "Francophones", "Bamileke", "separatists", "government", "tribal"]
            templates = [
                f"All {{topic}} should leave our country immediately!",
                f"{{topic}} are destroying our nation with their agenda",
                f"We need to take action against these {{topic}} before it's too late",
                f"{{topic}} don't belong here and should be removed by force if necessary"
            ]
        elif content_type == "misinformation":
            topics = ["vaccines", "5G", "government conspiracy", "elections", "COVID", "cures"]
            templates = [
                f"Secret {{topic}} that the government doesn't want you to know",
                f"{{topic}} are actually designed to control our minds",
                f"The truth about {{topic}} that mainstream media won't tell you",
                f"{{topic}} are causing health problems that doctors won't admit"
            ]
        elif content_type == "harassment":
            templates = [
                "You're worthless and should disappear",
                "No one will miss you if you're gone",
                "I know where you live and I'm coming for you",
                "You should be ashamed of yourself for existing"
            ]
        elif content_type == "spam":
            templates = [
                "Make money fast with this one weird trick",
                "You've won a free iPhone! Click here to claim",
                "Lose 10kg in one week with this miracle supplement",
                "Earn $5000 monthly working from home"
            ]
        else:  # fake news
            templates = [
                "Celebrity dies in tragic accident",
                "Government announces free money for everyone",
                "Military coup happening right now",
                "Breaking: Major disaster strikes capital city"
            ]

        template = random.choice(templates)
        if "{topic}" in template:
            topic = random.choice(topics)
            content = template.format(topic=topic)
        else:
            content = template


        if urgency_level in ["high", "critical"]:
            intensifiers = ["URGENT: ", "ALERT: ", "WARNING: ", "CRITICAL: "]
            content = random.choice(intensifiers) + content

        return content