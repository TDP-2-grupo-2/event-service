from event_service.databases import reports_repository
from collections import Counter


class ReportsStatisticsHandler:

    report_motives = ["spam", "ilegal", "ofensivo", "premium", "discriminatorio"]
    event_types = ["CONFERENCIA", "TEATRO", "CINE", "SHOW", "CONCIERTO", "OTRO"]

    
    def get_report_motive_statistics(self, reports_db, from_date, to_date):

        ## devolver ordenado por mayor motivo
        reports_metrics = []
        reports_by_motives = reports_repository.get_reported_events_group_by_motive(reports_db, from_date, to_date)
        for motive in reports_by_motives:
            
            amount_of_report_by_type_event = list(Counter(motive['event_types_by_reason']).items())
            reports_metrics.append({"motive": motive['reason'], 
                                    "principal_type_of_event": amount_of_report_by_type_event[0][0],
                                    "amount_of_report_by_type_of_event": amount_of_report_by_type_event[0][1],
                                    "amount_of_total_report_by_motive": motive['amount_of_reports_per_reason_by_type'],
                                    "data": amount_of_report_by_type_event})

        return reports_metrics
        

    def get_event_types_statistics(self, reports_db, from_date, to_date):

        event_types = []
        reports_per_event_type_and_reasons = reports_repository.get_reports_reasons_percentage_per_event_type(reports_db, from_date, to_date)
        for report in reports_per_event_type_and_reasons:
            
            amount_of_report_by_reason = list(Counter(report['report_reason_by_event_type']).items())
            event_types.append({"event_type": report['event_type'], 
                                    "principal_report_motive": amount_of_report_by_reason[0][0],
                                    "amount_of_reports_by_report_motive": amount_of_report_by_reason[0][1],
                                    "amount_of_total_report_by_type": report['amount_of_reports_per_event_type_by_reason'],
                                    "data": amount_of_report_by_reason})

        return event_types
    
