import SwiftUI

@main
class Main {
    static func main() {
        let he = HealthExporter()
        
        while true {
            he.export()
            sleep(3600)
        }
    }
}
