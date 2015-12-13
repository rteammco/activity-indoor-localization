//
//  DataPoint.swift
//  BWI Sensors
//
//  Created by Richard Teammco on 10/20/15.
//  Copyright © 2015 Richard Teammco. All rights reserved.
//

import Foundation
import CoreData

@objc(DataPoint)
class DataPoint: NSManagedObject {
    
    // attributes
    @NSManaged var accx: NSNumber
    @NSManaged var accy: NSNumber
    @NSManaged var accz: NSNumber
    @NSManaged var rotx: NSNumber
    @NSManaged var roty: NSNumber
    @NSManaged var rotz: NSNumber
    @NSManaged var loc_changed: Bool
    @NSManaged var loc_alt: NSNumber
    @NSManaged var loc_flr: NSNumber
    @NSManaged var loc_lat: NSNumber
    @NSManaged var loc_lon: NSNumber
    @NSManaged var compass_x: NSNumber
    @NSManaged var compass_y: NSNumber
    @NSManaged var compass_z: NSNumber
    @NSManaged var time: NSDate
    
}
