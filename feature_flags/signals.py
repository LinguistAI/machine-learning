

# myapp/signals.py
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Conversation
from .models import FeatureCategory, Feature, UserFeature
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=FeatureCategory)
def feature_category_created(sender, instance: FeatureCategory, created: bool, **kwargs):
    if created:
        logger.info(f"FeatureCategory created: {instance.name}")


@receiver(post_save, sender=Feature)
def feature_created_or_updated(sender, instance: Feature, created: bool, **kwargs) -> None:
    if instance.enabled:
        rollout_percentage = instance.rollout_percentage
        # Fetch all user emails from Conversation
        user_emails = list(Conversation.objects.values_list('userEmail', flat=True))

        # Calculate the number of users to roll out the feature to
        total_users = len(user_emails)
        new_rollout_count = int(total_users * (rollout_percentage / 100.0))

        # Fetch currently rolled out user emails
        current_rollout_emails = set(UserFeature.objects.filter(feature=instance, enabled=True).values_list('email', flat=True))

        if new_rollout_count > len(current_rollout_emails):
            # Increase rollout: add additional users
            additional_count = new_rollout_count - len(current_rollout_emails)
            potential_emails = set(user_emails) - current_rollout_emails
            new_emails = set(random.sample(potential_emails, additional_count))
            for email in new_emails:
                UserFeature.objects.update_or_create(email=email, feature=instance, defaults={'enabled': True})

        elif new_rollout_count < len(current_rollout_emails):
            # Decrease rollout: remove users
            excess_count = len(current_rollout_emails) - new_rollout_count
            remove_emails = set(random.sample(current_rollout_emails, excess_count))
            UserFeature.objects.filter(email__in=remove_emails, feature=instance).update(enabled=False)

        # Ensure all users have UserFeature entries, setting enabled to False for those not included
        existing_user_emails = set(UserFeature.objects.filter(feature=instance).values_list('email', flat=True))
        new_user_emails = set(user_emails) - existing_user_emails
        for email in new_user_emails:
            UserFeature.objects.create(email=email, feature=instance, enabled=False)

    else:
        # Disable the feature for all associated UserFeature objects if the feature is disabled
        UserFeature.objects.filter(feature=instance).update(enabled=False)

    # Update UserFeature objects enable field if feature is enabled or disabled
    UserFeature.objects.filter(feature=instance).update(enabled=instance.enabled)
        

            
            

@receiver(post_save, sender=UserFeature)
def user_feature_created(sender, instance: UserFeature, created: bool, **kwargs):
    if created:
        logger.info(f"UserFeature created: {instance.email} - {instance.feature.name}")


