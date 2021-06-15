import SwiftUI
import HealthKit

struct ContentView: View {
    var healthExporter = HealthExporter()
    @State var sessions: [HealthExporter.SleepSession] = []
    
    var body: some View {
        if healthExporter.error != "" {
            Text("error: " + healthExporter.error)
        } else {
            let _ = print(healthExporter.sessions)
            ForEach(healthExporter.sessions){ session in
                Text(session.id)
                Text("some")
            }
            Button("some"){
                healthExporter.fillSleepSessions()
            }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
