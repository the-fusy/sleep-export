import Foundation
import HealthKit
import Combine
import SwiftUI

class HealthExporter {
    var healthStore: HKHealthStore
    var sleepAnalysis = HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!
    var error = ""
    var sessions: [SleepSession] = []
    
    init() {
        healthStore = HKHealthStore()
        if !HKHealthStore.isHealthDataAvailable() {
            self.handleError(error: "health data is not available on device")
        }
        healthStore.requestAuthorization(toShare: Set(), read: Set([sleepAnalysis])) {
            success, error in
            if !success || error != nil {
                self.handleError(error: "don't have enough permissions to work properly")
            }
            // by the way, we can't check status of read permission
        }
    }
    
    func handleError(error: String) {
        self.error = error
    }
    
    struct SleepSession: Identifiable {
        var id: String
        var startDate: Date
        var endDate: Date
    }
    
    func fillSleepSessions() {
        let query = HKSampleQuery(sampleType: sleepAnalysis, predicate: nil, limit: 10, sortDescriptors: [NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)]) {
            _, results, error in
            if error != nil {
                self.handleError(error: "can't get sleep sessions")
                return
            }
            
            for item in results! {
                let sample = item as! HKCategorySample
                if sample.value != HKCategoryValueSleepAnalysis.inBed.rawValue {
                    continue
                }
                let session = SleepSession(id: sample.uuid.uuidString, startDate: sample.startDate, endDate: sample.endDate)
                self.sessions.append(session)
            }
            return
        }
        healthStore.execute(query)
    }
}
