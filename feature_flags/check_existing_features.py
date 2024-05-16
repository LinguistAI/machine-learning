

from feature_flags.models import Feature, UserFeature
import logging

logger = logging.getLogger(__name__)


def check_existing_features(email: str):
    # Check if the given email has UserFeature objects for all Feature objects
    features = Feature.objects.all()
    user_features = UserFeature.objects.filter(email=email)
    feature_names = [f.name for f in features]
    user_feature_names = [uf.feature.name for uf in user_features]
    
    missing_features = set(feature_names) - set(user_feature_names)
    
    new_features = []
    
    # Create the missing UserFeature objects
    for feature in missing_features:
        feature_obj = Feature.objects.get(name=feature)
        isEnabled = feature_obj and feature_obj.enabled and feature_obj.rollout_percentage == 100
        new_features.append(UserFeature.objects.create(email=email, feature=feature_obj, enabled=isEnabled))
        logger.info(f"Created UserFeature for email: {email}, feature: {feature}")
    
    return new_features
        

    
    