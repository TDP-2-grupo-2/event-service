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
    today = datetime.date.today().isoformat();
    event_report["event_name"] = reported_event["name"]
    event_report["event_description"] = reported_event["description"]
    event_report["event_type"] = reported_event["eventType"]
    event_report["user_name"] = user_info.name
    event_report["report_date"] = today
    event_report["user_email"] = user_info.email
    event_report["eventStatus"] = reported_event["status"]
    event_report["organizer_id"] = reported_event["ownerId"]
    event_report["organizer_name"] = reported_event["ownerName"]
    event_report["user_reporter_id"] = user_reporter_id

    new_event_report = reports_db["event_reports"].insert_one(event_report)
    report_created = reports_db["event_reports"].find_one(filter={"_id": new_event_report.inserted_id}, projection={'organizer_id':0, 'user_reporter_id':0})
    return json.loads(json_util.dumps(report_created))


def get_reporting_events(reports_db: Session, from_date: datetime.date = None, to_date: datetime.date = None):
    pipeline = []
    pipeline.append({"$match": {"eventStatus": {"$eq":"active"}}})
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

    final_projection = { "$project" : {"event_name": "$_id.event_name", "event_description": "$_id.event_description",
                                       "organizer_name": "$_id.organizer_name",  "event_id": "$_id.event_id", "organizer_id": "$_id.organizer_id",
                                        "_id": 0,  "amount_of_reports_per_reason": 1,  "reason": "$_id.reason"
                                        }}
    pipeline.append({"$sort": {"organizer_id": 1, "event_id": 1}})
    pipeline.append(group_by_events_and_reason_of_the_report)
    pipeline.append(final_projection)
    pipeline.append({"$sort": {"organizer_id": 1}})
    reports = reports_db["event_reports"].aggregate(pipeline)

    reports = list(json.loads(json_util.dumps(reports)))
    organizer_id = -1
    event_id = -1

    organizer_ids = []
    events_ids = []
    final_reports = []


    for doc in reports:
        if doc['organizer_id'] != organizer_id:
            organizer_ids.append(doc['organizer_id'])
            organizer_id = doc['organizer_id']
        if doc['event_id'] != event_id:
            events_ids.append(doc['event_id'])
            event_id = doc['event_id']
    # necesario para que no falle porque a veces se duplican los ids

    events_ids = list(dict.fromkeys(events_ids))

    for user_id in organizer_ids:
        for event_id in events_ids:
            amount_reports_reason = 0
            amount_reports = 0
            doc_to_save = {}
            for doc in reports: 
                if doc['organizer_id'] == user_id:
                    if doc['event_id'] == event_id: 
                        amount_reports += doc['amount_of_reports_per_reason']
                        if amount_reports_reason < doc['amount_of_reports_per_reason']:
                            amount_reports_reason = doc['amount_of_reports_per_reason']
                            doc_to_save['most_frecuent_reason'] = doc['reason']
                            doc_to_save['event_id'] = doc['event_id']
                            doc_to_save['event_name'] = doc['event_name']
                            doc_to_save['event_description'] = doc['event_description']
                            doc_to_save['organizer_name'] = doc['organizer_name']
                            doc_to_save['organizer_name'] = doc['organizer_name']
                            doc_to_save['organizer_id'] = doc['organizer_id']
                doc_to_save['amount_of_reports'] = amount_reports
        
            final_reports.append(doc_to_save)
    sorted_final_reports = sorted(final_reports, key=lambda x: x['amount_of_reports'], reverse=True)
    return sorted_final_reports


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
    final_projection = { "$project" : {"user_reporter_id": "$_id.user_reporter_id", "user_name": "$_id.user_name", "user_email": "$_id.user_email", "_id": 0,  "amount_of_reports_per_reason": 1,  "reason": "$_id.reason"}}
    pipeline.append(group_by_attendee_and_reason_of_report)
    pipeline.append(final_projection)
    pipeline.append({"$sort": {"user_reporter_id": 1}})
    reports = reports_db["event_reports"].aggregate(pipeline)
    reports = list(json.loads(json_util.dumps(reports)))


    id = -1
    ids = []
    final_reports = []


    for doc in reports:
        if doc['user_reporter_id'] != id:
            ids.append(doc['user_reporter_id'])
            id = doc['user_reporter_id']


    for user_id in ids:
        amount_reports_reason = 0
        amount_reports = 0
        doc_to_save = {}
        for doc in reports: 
            if doc['user_reporter_id'] == user_id:
                amount_reports += doc['amount_of_reports_per_reason']
                if amount_reports_reason < doc['amount_of_reports_per_reason']:
                    amount_reports_reason = doc['amount_of_reports_per_reason']
                    doc_to_save['most_frecuent_reason'] = doc['reason']
                    doc_to_save['user_email'] = doc['user_email']
                    doc_to_save['user_name'] = doc['user_name']
                doc_to_save['amount_of_reports'] = amount_reports
        
        final_reports.append(doc_to_save)
    sorted_final_reports = sorted(final_reports, key=lambda x: x['amount_of_reports'], reverse=True)


    return sorted_final_reports

def update_events_status_by_organizer(reports_db, organizer_id):
    reports_db['event_reports'].update_many({"organizer_id": organizer_id}, {"$set": {'eventStatus': "canceled"}})
    result=reports_db["event_reports"].find({"organizer_id": organizer_id})

def update_events_status_by_event_id(reports_db, event_id):
    reports_db['event_reports'].update_many({"event_id": event_id}, {"$set": {'eventStatus': "canceled"}})
    result=reports_db["event_reports"].find({"event_id": event_id})

def delete_all_data(reports_db):
    reports_db['event_reports'].delete_many({})


def add_date_filter(pipeline, from_date, date_field: str, date_range: str):
    if from_date is not None:
        from_date_formatted = from_date.isoformat()
        pipeline.append({"$match": {date_field: {date_range: from_date_formatted}}})


def get_reported_events_group_by_motive(reports_db, from_date, to_date):
    pipeline = []

    if from_date is not None:
        from_date_formatted = from_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$gte": from_date_formatted}}})

    if to_date is not None:
        to_date_formatted = to_date.isoformat()
        pipeline.append({"$match": {"report_date": {"$lte": to_date_formatted}}})

    group_by_motive = {"$group": {
                            "_id": {
                                "reason": "$reason",
                                },
                            "event_types_by_reason": {"$push": "$event_type"},                  
                            "amount_of_reports_per_reason_by_type": {"$sum": 1}
                        }}
    

    final_projection = { "$project" : {"reason": "$_id.reason", "event_types_by_reason": 1, "_id": 0,  "amount_of_reports_per_reason_by_type": 1}}
    sort = {"$sort": {"amount_of_reports_per_reason_by_type": -1}}
    pipeline.append(group_by_motive)
    pipeline.append(final_projection)
    pipeline.append(sort)
    reports = reports_db["event_reports"].aggregate(pipeline)
    reports = list(json.loads(json_util.dumps(reports)))
    return reports
    

def group_by_reports_type(pipeline):
    pipeline.append({"$group": {
                            "_id": {
                                "event_type": "$event_type",
                                },
                            "report_reason_by_event_type": {"$push": "$reason"},                  
                            "amount_of_reports_per_event_type_by_reason": {"$sum": 1}
                        }})
    

def project_reports_types_and_motives(pipeline):
    pipeline.append({ "$project" : {"event_type": "$_id.event_type", "report_reason_by_event_type": 1, "_id": 0,  "amount_of_reports_per_event_type_by_reason": 1}})


def exec_pipeline(pipeline, reports_db, collection: str):
    result = reports_db[collection].aggregate(pipeline)
    result = list(json.loads(json_util.dumps(result)))
    return result


def get_reports_reasons_percentage_per_event_type(reports_db, from_date, to_date):
    pipeline = []
    add_date_filter(pipeline, from_date, "report_date", "$gte")
    add_date_filter(pipeline, to_date, "report_date", "$lte")
    group_by_reports_type(pipeline)
    project_reports_types_and_motives(pipeline)
    pipeline.append({"$sort": {"amount_of_reports_per_event_type_by_reason": -1}})
    result = exec_pipeline(pipeline, reports_db, "event_reports")
    return result
