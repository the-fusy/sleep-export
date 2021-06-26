import Foundation
import HealthKit
import Combine
import SwiftUI

class HealthExporter {
    var healthStore: HKHealthStore
    var sleepAnalysis = HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!
    
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
    
    struct SleepSession: Codable {
        var id: String
        var startDate: Date
        var endDate: Date
        
        enum CodingKeys: String, CodingKey {
            case id
            case startDate = "start_date"
            case endDate = "end_date"
        }

        func encode(to encoder: Encoder) throws {
            var container = encoder.container(keyedBy: CodingKeys.self)
            try container.encode(id, forKey: .id)
            try container.encode(startDate, forKey: .startDate)
            try container.encode(endDate, forKey: .endDate)
        }
    }
    
    struct ExportData: Codable {
        var sleepSessions: [SleepSession]?
        var error: String?
        
        enum CodingKeys: String, CodingKey {
            case sleepSessions = "sleep_sessions"
            case error
        }
        
        func encode(to encoder: Encoder) throws {
            var container = encoder.container(keyedBy: CodingKeys.self)
            try container.encode(sleepSessions, forKey: .sleepSessions)
            try container.encode(error, forKey: .error)
        }
    }
    
    
    func handleError(error: String) {
        self.sendData(exportData: ExportData(error: error))
    }
    
    func export() {
        let query = HKSampleQuery(
            sampleType: sleepAnalysis,
            predicate: nil,
            limit: 100,
            sortDescriptors: [NSSortDescriptor(key: HKSampleSortIdentifierEndDate, ascending: false)]
        ) {
            _, results, error in
            if error != nil {
                self.handleError(error: "can't get sleep sessions")
                return
            }
            
            var sessions: [SleepSession] = []
            for item in results! {
                let sample = item as! HKCategorySample
                if sample.value != HKCategoryValueSleepAnalysis.inBed.rawValue {
                    continue
                }
                let session = SleepSession(id: sample.uuid.uuidString, startDate: sample.startDate, endDate: sample.endDate)
                sessions.append(session)
            }
            
            if sessions.count == 0 {
                self.handleError(error: "empty set of sessions, maybe it's not enough read permissions")
            }
            
            self.sendData(exportData: ExportData(sleepSessions: sessions))
        }
        healthStore.execute(query)
    }
    
    func sendData(exportData: ExportData) {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(exportData) else {
            self.handleError(error: "can't encode data: " + String(reflecting: exportData))
            return
        }
        
        let url = URL(string: "https://functions.yandexcloud.net/...")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let task = URLSession.shared.uploadTask(with: request, from: data) {
            _, response, error in
            if error != nil {
                return
            }
        }
        task.resume()
    }
}
