//
//  AppData.swift
//  BWI Sensors
//
//  Created by Richard Teammco on 11/13/15.
//  Copyright © 2015 Richard Teammco. All rights reserved.
//

import Foundation
import CoreData

@objc(AppData)
class AppData: NSManagedObject {
    
    // attributes
    @NSManaged var samples_per_sec: Int32
    
}
