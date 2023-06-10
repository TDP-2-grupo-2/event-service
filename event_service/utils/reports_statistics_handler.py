from event_service.databases import event_repository, reports_repository
from collections import Counter




class ReportsStatisticsHandler:
    
    def get_report_motive_statistics(self, reports_db, event_db, from_date, to_date):
        ## devolver ordenado por mayor motivo
        reports_metrics = []
        reports_by_motives = reports_repository.get_reported_events_group_by_motive(reports_db, from_date, to_date)
        #print(reports_by_motives)
        for motive in reports_by_motives:
            
            amount_of_report_by_type_event = list(Counter(motive['event_types_by_reason']).items())
            #print(amount_of_report_by_type_event)
            #print(len(amount_of_report_by_type_event))
            #print(amount_of_report_by_type_event[0][0])
            reports_metrics.append({"motive": motive['reason'], 
                                    "principal_type_of_event": amount_of_report_by_type_event[0][0],
                                    "amount_of_report_by_type_of_event": amount_of_report_by_type_event[0][1],
                                    "amount_of_total_report_by_motive": motive['amount_of_reports_per_reason_by_type'],
                                    "data": amount_of_report_by_type_event})

        return reports_metrics