from datetime import datetime

from pydantic import BaseModel

from common.enums import NotificationStatus


class NotificationSchema(BaseModel):
    id: int
    recipient_id: int
    text: str
    status: NotificationStatus = NotificationStatus.SENT.value
    created_at: datetime = None
    published_at: datetime = None


class NotificationWSSchema(BaseModel):
    id: int
    text: str
    status: NotificationStatus = NotificationStatus.SENT.value
    created_at: datetime = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
