
from typing import Optional
from event_service.exceptions import exceptions
from event_service.databases import event_repository
from numpy import log as ln
import math


class EventsStatisticsHandler:

    event_types = ["CONFERENCIA", "TEATRO", "CINE", "SHOW", "CONCIERTO", "OTRO"]
    event_status = {"suspended":"suspendido", "active": "activo", "canceled": "cancelado", "finalized": "finalizado"}

    def get_events_status_statistics(self, event_db, from_date, to_date):
        grouped_event_status = event_repository.get_events_statistics_by_event_status(event_db, from_date, to_date)
        event_status_statistics = {}
        print(grouped_event_status)


        if grouped_event_status == []:
            return event_status_statistics
        
        for status_result in grouped_event_status:
            event_status = status_result["status"]
            event_status_statistics[event_status] = status_result["amount_per_status"]

        grouped_event_status_keys = event_status_statistics.keys()

        for event_status_key in self.event_status.keys():
            if event_status_key not in grouped_event_status_keys:
                event_status_statistics[self.event_status[event_status_key]] = 0
            else:
                event_status_statistics[self.event_status[event_status_key]] = event_status_statistics[event_status_key]
                del event_status_statistics[event_status_key]
        

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
    
    def get_registered_entries_amount_per_event(self, event_db, from_date, to_date):
            events = event_repository.get_registered_entries_amount_per_timestamp(event_db, from_date, to_date)
            return events


    def get_top_organizers_statistics(self, event_db):
        
        top_organizers = []
        group_organizer_by_event = event_repository.get_organizer_group_by_events(event_db)
        for orgaganizer_events in group_organizer_by_event:

            
            coefficient = 0
            relation_entries_capacity = 0
            for event in orgaganizer_events['events']: 

                event_entries_amount = event_repository.get_amount_of_event_registered_entries(event_db, event['eventId']['$oid'])

                relation_entries_capacity+= event_entries_amount/event['capacity']
            
            coefficient = ((relation_entries_capacity*ln(orgaganizer_events['amount_of_events'] + 0.01))/(math.e))*100
            print(coefficient)
            
            top_organizers.append({'ownerName': orgaganizer_events['ownerName'], 'coeficient': coefficient})

        top_organizers = sorted(top_organizers, key=lambda d: d['coeficient'], reverse=True) 

        return top_organizers[:5]

