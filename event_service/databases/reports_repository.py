import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from event_service.databases import event_repository
from event_service.exceptions import exceptions
from typing import Union, List
from sqlalchemy.orm import Session


def report_event(user_reporter_id: str, event_report: dict, reports_db: Session, events_db: Session):
    reported_event = event_repository.get_event_by_id(event_report["event_id"], events_db)
    existing_report = reports_db["event_reports"].find_one({"user_reporter_id": user_reporter_id, "event_id": event_report['event_id']})
    if existing_report is not None:
        raise exceptions.AlreadyReportedEvent
    
    event_report["organizer_id"] = reported_event["ownerId"]
    event_report["user_reporter_id"] = user_reporter_id
    print(event_report["user_reporter_id"],  event_report["organizer_id"] )

    new_event_report = reports_db["event_reports"].insert_one(event_report)
    report_created = reports_db["event_reports"].find_one({"_id": new_event_report.inserted_id})
    return json.loads(json_util.dumps(report_created))


    



