
from typing import Optional
from event_service.exceptions import exceptions
from event_service.databases import event_repository


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

