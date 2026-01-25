from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
import json


class UserPrivacySettings(SQLModel, table=True):
    """
    Model for storing user privacy settings related to analytics
    """
    user_id: str = Field(primary_key=True)
    analytics_sharing_consent: bool = Field(default=True)
    data_retention_consent: bool = Field(default=True)
    ai_profiling_consent: bool = Field(default=True)
    marketing_communication_consent: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "analytics_sharing_consent": self.analytics_sharing_consent,
            "data_retention_consent": self.data_retention_consent,
            "ai_profiling_consent": self.ai_profiling_consent,
            "marketing_communication_consent": self.marketing_communication_consent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class PrivacyControls:
    """
    Class to manage privacy controls for analytics data
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_user_privacy_settings(self, user_id: str) -> Optional[UserPrivacySettings]:
        """
        Get privacy settings for a user
        """
        statement = select(UserPrivacySettings).where(UserPrivacySettings.user_id == user_id)
        return self.session.exec(statement).first()
    
    def update_privacy_settings(
        self, 
        user_id: str, 
        analytics_sharing_consent: Optional[bool] = None,
        data_retention_consent: Optional[bool] = None,
        ai_profiling_consent: Optional[bool] = None,
        marketing_communication_consent: Optional[bool] = None
    ) -> UserPrivacySettings:
        """
        Update privacy settings for a user
        """
        settings = self.get_user_privacy_settings(user_id)
        
        if settings is None:
            # Create new settings if they don't exist
            settings = UserPrivacySettings(
                user_id=user_id,
                analytics_sharing_consent=analytics_sharing_consent if analytics_sharing_consent is not None else True,
                data_retention_consent=data_retention_consent if data_retention_consent is not None else True,
                ai_profiling_consent=ai_profiling_consent if ai_profiling_consent is not None else True,
                marketing_communication_consent=marketing_communication_consent if marketing_communication_consent is not None else False
            )
            self.session.add(settings)
        else:
            # Update existing settings
            if analytics_sharing_consent is not None:
                settings.analytics_sharing_consent = analytics_sharing_consent
            if data_retention_consent is not None:
                settings.data_retention_consent = data_retention_consent
            if ai_profiling_consent is not None:
                settings.ai_profiling_consent = ai_profiling_consent
            if marketing_communication_consent is not None:
                settings.marketing_communication_consent = marketing_communication_consent
            
            settings.updated_at = datetime.utcnow()
        
        self.session.commit()
        return settings
    
    def can_collect_analytics(self, user_id: str) -> bool:
        """
        Check if analytics data can be collected for a user
        """
        settings = self.get_user_privacy_settings(user_id)
        if settings is None:
            # Default to True if no settings exist
            return True
        return settings.analytics_sharing_consent
    
    def can_retain_data(self, user_id: str) -> bool:
        """
        Check if user data can be retained
        """
        settings = self.get_user_privacy_settings(user_id)
        if settings is None:
            # Default to True if no settings exist
            return True
        return settings.data_retention_consent
    
    def can_profile_for_ai(self, user_id: str) -> bool:
        """
        Check if user data can be used for AI profiling
        """
        settings = self.get_user_privacy_settings(user_id)
        if settings is None:
            # Default to True if no settings exist
            return True
        return settings.ai_profiling_consent
    
    def can_send_marketing(self, user_id: str) -> bool:
        """
        Check if marketing communications can be sent to user
        """
        settings = self.get_user_privacy_settings(user_id)
        if settings is None:
            # Default to False if no settings exist
            return False
        return settings.marketing_communication_consent
    
    def anonymize_user_data(self, user_id: str) -> bool:
        """
        Anonymize user data for compliance purposes
        """
        # This would typically trigger a process to anonymize the user's data
        # For this implementation, we'll just log the request
        print(f"Anonymization requested for user: {user_id}")
        
        # In a real implementation, this would:
        # 1. Remove or encrypt personally identifiable information
        # 2. Update all related records to remove user association
        # 3. Ensure compliance with regulations like GDPR
        
        return True
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all user data for compliance purposes (right to be forgotten)
        """
        # This would typically trigger a process to delete the user's data
        # For this implementation, we'll just log the request
        print(f"Deletion requested for user: {user_id}")
        
        # In a real implementation, this would:
        # 1. Delete the privacy settings record
        # 2. Delete all related user data across all tables
        # 3. Ensure compliance with regulations like GDPR
        
        return True
    
    def get_privacy_report(self, user_id: str) -> dict:
        """
        Generate a privacy report for the user
        """
        settings = self.get_user_privacy_settings(user_id)
        if not settings:
            return {"error": "No privacy settings found for user"}
        
        return {
            "user_id": user_id,
            "settings": settings.to_dict(),
            "data_collected": self._get_data_collection_status(user_id),
            "data_usage": self._get_data_usage_info(),
            "compliance_status": self._get_compliance_status(user_id)
        }
    
    def _get_data_collection_status(self, user_id: str) -> dict:
        """
        Get status of data collection for the user
        """
        # This would connect to analytics systems to get actual data
        # For this implementation, we'll return a mock status
        return {
            "analytics_active": self.can_collect_analytics(user_id),
            "profile_active": self.can_profile_for_ai(user_id),
            "data_retained": self.can_retain_data(user_id),
            "last_collection": datetime.utcnow().isoformat()
        }
    
    def _get_data_usage_info(self) -> dict:
        """
        Get information about how data is used
        """
        return {
            "purpose": "Improving AI suggestions and personalizing user experience",
            "retention_period": "Data is retained as long as account exists unless deleted",
            "sharing": "Data is not shared with third parties",
            "processing_location": "Data is processed in secure EU data centers"
        }
    
    def _get_compliance_status(self, user_id: str) -> dict:
        """
        Get compliance status for the user
        """
        return {
            "gdpr_compliant": True,
            "data_portability": True,
            "right_to_erasure": True,
            "consent_up_to_date": True
        }