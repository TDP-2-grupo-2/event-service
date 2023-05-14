import json
import datetime
from bson import json_util
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from event_service.databases import event_repository, attende_repository
from event_service.exceptions import exceptions
from typing import Union, List
from sqlalchemy.orm import Session


def report_event(user_reporter_id: str, event_report: dict, reports_db: Session, events_db: Session, users_db: Session):
    reported_event = event_repository.get_event_by_id(event_report["event_id"], events_db)
    user_info = attende_repository.get_attendee_by_id(users_db, user_reporter_id)
    existing_report = reports_db["event_reports"].find_one({"user_reporter_id": user_reporter_id, "event_id": event_report['event_id']})
    if existing_report is not None:
        raise exceptions.AlreadyReportedEvent
    print(user_info)
    today = datetime.date.today().isoformat();
    event_report["event_name"] = reported_event["name"]
    event_report["event_description"] = reported_event["description"]
    event_report["user_name"] = user_info.name
    event_report["report_date"] = today
    event_report["user_email"] = user_info.email
    event_report["eventStatus"] = reported_event["status"]
    event_report["organizer_id"] = reported_event["ownerId"]
    event_report["organizer_name"] = reported_event["ownerName"]
    event_report["user_reporter_id"] = user_reporter_id
    print(event_report["user_reporter_id"],  event_report["organizer_id"] )

    new_event_report = reports_db["event_reports"].insert_one(event_report)
    report_created = reports_db["event_reports"].find_one(filter={"_id": new_event_report.inserted_id}, projection={'organizer_id':0, 'user_reporter_id':0})
    return json.loads(json_util.dumps(report_created))


def get_reporting_events(reports_db: Session, from_date: datetime.date = None, to_date: datetime.date = None):
    pipeline = []
   # pipeline.append({"$match": {"eventStatus": {"$eq":"active"}}})
    if from_date is not None:
        from_date_formatted = from_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$gte": from_date_formatted}}})

    if to_date is not None:
        to_date_formatted = to_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$lte": to_date_formatted}}})
    group_by_events_and_reason_of_the_report = {"$group": {
                            "_id": {
                                "event_name": "$event_name", 
                                "event_description": "$event_description",
                                "event_id": "$event_id",
                                "organizer_id": "$organizer_id",
                                "organizer_name": "$organizer_name",
                                "reason": "$reason"
                                },                
                            "amount_of_reports_per_reason": {"$sum": 1}
                        }}
    sort_by_most_frecuent_reporting_reason = {"$sort": {"_id.event_id": -1, "amount_of_reports_per_reason": -1}}

    group_by_reason = {"$group": {
                            "_id": {
                                "event_id": "$_id.event_id",
                                "event_name": "$_id.event_name", 
                                "event_description": "$_id.event_description",
                                "organizer_name": "$_id.organizer_name",
                                "organizer_id": "$_id.organizer_id",
                                },             
                            "amount_of_reports": {"$sum": "$amount_of_reports_per_reason"},
                            "most_frecuent_reason": {"$first": "$_id.reason"}        
                        }}
    
    rank_by_amount_of_reports = {"$sort": {"amount_of_reports": -1}}
    final_projection = { "$project" : {"event_name": "$_id.event_name", "event_description": "$_id.event_description",
                                       "organizer_name": "$_id.organizer_name",  "id": "$_id.event_id", "organizer_id": "$_id.organizer_id",
                                        "_id": 0,  "amount_of_reports": 1,  "most_frecuent_reason": 1
                                        }}
    pipeline.append(group_by_events_and_reason_of_the_report)
    pipeline.append(sort_by_most_frecuent_reporting_reason)
    pipeline.append(group_by_reason)
    pipeline.append(rank_by_amount_of_reports)
    pipeline.append(final_projection)
    reports = reports_db["event_reports"].aggregate(pipeline)

    return list(json.loads(json_util.dumps(reports)))


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


def update_event_status(reports_db, event_id):
    reports_db['event_reports'].update_many({"event_id": event_id}, {"$set": {'eventStatus': "canceled"}})
    result=reports_db["event_reports"].find({"event_id": event_id})

def update_events_status_by_organizer(reports_db, organizer_id):
    reports_db['event_reports'].update_many({"organizer_id": organizer_id}, {"$set": {'eventStatus': "canceled"}})
    result=reports_db["event_reports"].find({"organizer_id": organizer_id})