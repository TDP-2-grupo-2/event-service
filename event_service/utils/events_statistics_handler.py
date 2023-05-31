
from event_service.exceptions import exceptions
from event_service.databases import event_repository


class EventsStatisticsHandler:

    def get_events_status_statistics(self, event_db):

        #group by timestamp y event status y devuelvo cantidad de eventos con ese estado en ese dia?
        return 1
    
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

