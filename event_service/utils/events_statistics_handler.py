
from typing import Optional
from event_service.exceptions import exceptions
from event_service.databases import event_repository


class EventsStatisticsHandler:

    event_types = ["CONFERENCIA", "TEATRO", "CINE", "SHOW", "CONCIERTO", "OTRO"]

    def get_events_types_statistics(self, event_db, from_date, to_date):
        grouped_event_types = event_repository.get_events_statistics_by_event_type(event_db, from_date, to_date)
        event_type_statistics = {}
        for type_result in grouped_event_types:
            event_type = type_result["type"]
            event_type_statistics[event_type] = type_result["amount_per_type"]
        
        grouped_event_types_keys = event_type_statistics.keys()

        for event_type in self.event_types:
            if event_type not in grouped_event_types_keys:
                event_type_statistics[event_type] = 0

        return event_type_statistics
    
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

