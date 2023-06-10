from event_service.databases import event_repository, reports_repository





class ReportsStatisticsHandler:
    
    def get_report_motive_statistics(self, reports_db, event_db, from_date, to_date):

        reports = reports_repository.get_reported_events_group_by_motive(reports_db, from_date, to_date)
        print(reports)
        return reports