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
    report_created = reports_db["event_reports"].find_one(filter={"_id": new_event_report.inserted_id}, projection={'organizer_id':0, 'user_reporter_id':0})
    return json.loads(json_util.dumps(report_created))


def get_reporting_attendees(reports_db: Session, from_date: datetime.date = None, to_date: datetime.date = None):
    pipeline = []

    if from_date is not None:
        from_date_formatted = from_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$gte": from_date_formatted}}})

    if to_date is not None:
        to_date_formatted = to_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$lte": to_date_formatted}}})

    group_by_attendee_and_reason_of_report = {"$group": {
                            "_id": {
                                "user_name": "$user_name", 
                                "user_email": "$user_email",
                                "user_reporter_id": "$user_reporter_id",
                                "reason": "$reason"
                                },                     
                            "amount_of_reports_per_reason": {"$sum": 1}
                        }}
    sort_by_most_frecuent_reporting_reason = {"$sort": {"_id.user_reporter_id": 1, "amount_of_reports": 1}}

    group_by_reason = {"$group": {
                            "_id": {
                                "user_name": "$_id.user_name", 
                                "user_email": "$_id.user_email",
                                },                     
                            "amount_of_reports": {"$sum": "$amount_of_reports_per_reason"},
                            "most_frecuent_reason": {"$first": "$_id.reason"}        
                        }}
    
    rank_by_amount_of_reports = {"$sort": {"amount_of_reports": -1}}
    final_projection = { "$project" : {"user_name": "$_id.user_name", "user_email": "$_id.user_email", "_id": 0,  "amount_of_reports": 1,  "most_frecuent_reason": 1}}
    pipeline.append(group_by_attendee_and_reason_of_report)
    pipeline.append(sort_by_most_frecuent_reporting_reason)
    pipeline.append(group_by_reason)
    pipeline.append(rank_by_amount_of_reports)
    pipeline.append(final_projection)
    reports = reports_db["event_reports"].aggregate(pipeline)
    return list(json.loads(json_util.dumps(reports)))


    



