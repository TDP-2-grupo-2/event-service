
import datetime
from typing import Optional
from event_service.exceptions import exceptions
from event_service.databases import event_repository

import math


class EventsStatisticsHandler:

    event_types = ["CONFERENCIA", "TEATRO", "CINE", "SHOW", "CONCIERTO", "OTRO"]
    event_status = {"suspended":"suspendido", "active": "activo", "canceled": "cancelado", "finalized": "finalizado", "draft": "borrador"}

    def get_events_status_statistics(self, event_db, from_date, to_date):
        grouped_published_events_status = event_repository.get_events_statistics_by_event_status(event_db, from_date, to_date)
        event_status_statistics = {}

        if grouped_published_events_status == []:
            return event_status_statistics
        
        for status_result in grouped_published_events_status:
            event_status = status_result["status"]
            event_status_statistics[event_status] = status_result["amount_per_status"]

        grouped_event_status_keys = event_status_statistics.keys()

        # translation
        for event_status_key in self.event_status.keys():
            event_status_statistics[self.event_status[event_status_key]] = 0
            if event_status_key in grouped_event_status_keys:
                event_status_statistics[self.event_status[event_status_key]] = event_status_statistics[event_status_key]
                del event_status_statistics[event_status_key]
        
        amount_draft_events = event_repository.get_amount_drafts_statistics(event_db, from_date, to_date)

        event_status_statistics[self.event_status["draft"]] = amount_draft_events

        return event_status_statistics

    
    def get_event_registered_entries_statistics(self, event_db, event_id, organizer_id):
        event = event_repository.get_event_by_id(event_id, event_db)
        event_capacity = event['capacity']
        event_attendance = event['attendance']

        if event['ownerId'] != organizer_id:
            raise exceptions.UnauthorizeUser
            
        event_entries = event_repository.get_event_registered_entries_per_timestamp(event_db, event_id)
        event_current_registered_attendance = 0

        for registry in event_entries:
            event_current_registered_attendance += registry['amount_of_entries']

        statistics = {
            'entries': event_entries,
            'current_registered_attendance': event_current_registered_attendance,
            'capacity': event_capacity,
            'attendance': event_attendance,
            'event_id': event_id
        }
        
        return statistics

    def change_registered_entries_scale(self, entries, previous_date_format:str, new_date_format: str, date_field: str, count_field: str):
        previous_date = 0
        dates = []
        for entry in entries:
            actual_date = datetime.datetime.strptime(entry[date_field], previous_date_format)
            entry_date = actual_date.strftime(new_date_format)
            if previous_date != entry_date:
                dates.append(entry_date)
                previous_date = entry_date
        
        formatted_events = []

        for date in dates:
            date_document = {
                date_field: date,
                count_field: 0
            }

            for entry in entries:
                actual_date = datetime.datetime.strptime(entry[date_field], previous_date_format)
                entry_date = actual_date.strftime(new_date_format)

                if date == entry_date:    
                    date_document[count_field] += entry[count_field]

            formatted_events.append(date_document)

        return formatted_events
    
    def merge_grouped_events_by_timestamp(self, draft_events, published_events):

        j = 0
        i = 0
        amount_drafts = len(draft_events)
        amount_published = len(published_events)
        merged = []
        print(published_events)
        while i < amount_drafts and j < amount_published:
            if draft_events[i]["dateOfCreation"] == published_events[j]["dateOfCreation"]:
                amount_events = draft_events[i]["amount_of_events"] +  published_events[j]["amount_of_events"]
                merged.append({"dateOfCreation": draft_events[i]["dateOfCreation"], "amount_of_events": amount_events})
                i += 1
                j += 1

            elif datetime.fromtimestamp(draft_events[i]["dateOfCreation"]) < datetime.fromtimestamp(published_events[j]["amount_of_events"]):
                merged.append({"dateOfCreation": draft_events[i]["dateOfCreation"], "amount_of_events": draft_events[i]["amount_of_events"]})
                i += 1

            else:
                merged.append({"dateOfCreation": published_events[i]["amount_of_events"], "amount_of_events": published_events[i]["amount_of_events"]})
                j += 1


        while i < amount_drafts:
            merged.append({"dateOfCreation": draft_events[i]["dateOfCreation"], "amount_of_events": draft_events[i]["amount_of_events"]})
            i += 1


        while j < amount_published:
            merged.append({"dateOfCreation": published_events[i]["dateOfCreation"], "amount_of_events": published_events[i]["amount_of_events"]})
            j += 1

        print(merged)

        return merged


    def get_amount_events_per_timestamp(self, event_db, from_date, to_date):
            draft_events = event_repository.get_events_drafts_amount_per_timestamp(event_db, from_date, to_date)
            published_events = event_repository.get_events_amount_per_timestamp(event_db, from_date, to_date)
            formatted_draft_events = self.change_registered_entries_scale(draft_events, "%Y-%m-%d", "%Y-%m", "dateOfCreation", "amount_of_events")
            formatted_published_events = self.change_registered_entries_scale(published_events, "%Y-%m-%d", "%Y-%m", "dateOfCreation", "amount_of_events")
            merged_events_results = self.merge_grouped_events_by_timestamp(formatted_draft_events, formatted_published_events)
            return merged_events_results


    def get_registered_entries_amount_per_event(self, event_db, from_date, to_date, scale_type):
            events = event_repository.get_registered_entries_amount_per_timestamp(event_db, from_date, to_date)
            if scale_type == "years":
                formatted_events = self.change_registered_entries_scale(events, "%Y-%m-%d %H", "%Y", "entry_timestamp", "amount_of_entries")
                return formatted_events
            if scale_type == "months":
                formatted_events = self.change_registered_entries_scale(events, "%Y-%m-%d %H", "%Y-%m", "entry_timestamp", "amount_of_entries")
                return formatted_events
            if scale_type == "days":
                formatted_events = self.change_registered_entries_scale(events, "%Y-%m-%d %H", "%Y-%m-%d", "entry_timestamp", "amount_of_entries")
                return formatted_events
            return formatted_events


    def get_top_organizers_statistics(self, event_db):
        
        top_organizers = []
        group_organizer_by_event = event_repository.get_organizer_group_by_events(event_db)
        for orgaganizer_events in group_organizer_by_event:

            
            coefficient = 0
            relation_entries_capacity = 0
            for event in orgaganizer_events['events']: 

                event_entries_amount = event_repository.get_amount_of_event_registered_entries(event_db, event['eventId']['$oid'])

                relation_entries_capacity+= event_entries_amount/event['capacity']
            
            coefficient = ((relation_entries_capacity*math.log(orgaganizer_events['amount_of_events'] + 0.01))/(math.e))*100
            
            
            top_organizers.append({'ownerName': orgaganizer_events['ownerName'], 'coeficient': coefficient})

        top_organizers = sorted(top_organizers, key=lambda d: d['coeficient'], reverse=True) 

        return top_organizers[:5]
    


