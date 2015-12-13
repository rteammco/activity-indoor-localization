//
//  DataManager.swift
//  BWI Sensors
//
//  Created by Richard Teammco on 10/18/15.
//  Copyright © 2015 Richard Teammco. All rights reserved.
//

import CoreData
import Foundation
import UIKit

public class DataManager {
    
    // These are the most recent motion values.
    private var accXval: Double = 0
    private var accYval: Double = 0
    private var accZval: Double = 0
    private var rotXval: Double = 0
    private var rotYval: Double = 0
    private var rotZval: Double = 0
    
    // These are the most recent location values.
    private var locLat: Double = 0 // latitude
    private var locLon: Double = 0 // longitude
    private var locAlt: Double = 0 // altitude
    private var locFlr: Int = 0 // floor estimate
    private var locUpdated: Bool = false
    
    // These are the most recent compass values. These get updated upon motion.
    private var compassX: Double = 0
    private var compassY: Double = 0
    private var compassZ: Double = 0
    
    // This is the core data managed object (context) used for saving.
    let context = (UIApplication.sharedApplication().delegate as! AppDelegate).managedObjectContext
    
    // Data logging timer and rate values.
    private var logRate: Double = 0.05
    private var logging: Bool!
    private var logTimer: NSTimer!
    
    // Starts the logging timer, wich calls the "saveLastDataPoint" function every interval. If logging is not turned on, the function will not do anything.
    init() {
        logging = false
        resetTimer()
    }
    
    // Initializes the timer with the latest saved rate. The variable will be overwritten and invalidated if it already exists.
    private func resetTimer() {
        if (logTimer != nil) {
            logTimer.invalidate()
        }
        logTimer = NSTimer.scheduledTimerWithTimeInterval(logRate, target: self, selector: "saveLastDataPoint", userInfo: nil, repeats: true)
    }
    
    // Sets the sampling rate for the timer. Timer gets reset and the value will be saved for future reference.
    public func setSamplesPerSecond(var samplesPerSecond: Int32) {
        if (samplesPerSecond < 1) {
            samplesPerSecond = 1
        } else if (samplesPerSecond > 30) {
            samplesPerSecond = 30
        }
        logRate = 1.0 / Double(samplesPerSecond)
        resetTimer()
    }
    
    // Returns the sampling rate in terms of number of samples per second.
    public func getSamplesPerSecond() -> Int32 {
        return Int32(1.0 / logRate)
    }
    
    // Sets the next acceleration values.
    public func setAccPoint(accx: Double, accy: Double, accz: Double) {
        accXval = accx
        accYval = accy
        accZval = accz
    }
    
    // Sets the next rotation values.
    public func setRotPoint(rotx: Double, roty: Double, rotz: Double) {
        rotXval = rotx
        rotYval = roty
        rotZval = rotz
    }
    
    // Sets the next location values, and triggers location as updated for saving.
    public func setLocValues(lat: Double, lon: Double, alt: Double, flr: Int) {
        locLat = lat
        locLon = lon
        locAlt = alt
        locFlr = flr
        // TODO: might only need to update during significant changes?
        locUpdated = true
    }
    
    // Sets the next compass values. These will get saved during the next save interval.
    public func setCompassValues(x: Double, y: Double, z: Double) {
        compassX = x
        compassY = y
        compassZ = z
    }
    
    // Sets the logging state: if false, logging is not saved; otherwise, it is saved.
    public func setLoggingState(onOrOff: Bool) {
        logging = onOrOff
    }
    
    // Saves the data from the last acceleration and rotation points as updated.
    @objc func saveLastDataPoint() {
        if !logging {
            return
        }
        // Set the latest data point values.
        let dataPoint = NSEntityDescription.insertNewObjectForEntityForName("DataPoint", inManagedObjectContext: context) as! DataPoint
        dataPoint.accx = accXval
        dataPoint.accy = accYval
        dataPoint.accz = accZval
        dataPoint.rotx = rotXval
        dataPoint.roty = rotYval
        dataPoint.rotz = rotZval
        dataPoint.loc_alt = locAlt
        dataPoint.loc_flr = locFlr
        dataPoint.loc_lat = locLat
        dataPoint.loc_lon = locLon
        dataPoint.compass_x = compassX
        dataPoint.compass_y = compassY
        dataPoint.compass_z = compassZ
        dataPoint.loc_changed = locUpdated
        locUpdated = false
        dataPoint.time = NSDate() // Date (time) right now.
        // try to save the DataPoint.
        do {
            try context.save()
        } catch _ as NSError {
            // TODO: Log error?
            print("Failed to save DataPoint.")
        }
        print("Saved DataPoint.")
    }
    
    // Returns the number of data points currently stored in the app's storage.
    public func numberOfPoints() -> Int {
        // TODO: this probably really inefficient; is there a better way of getting a count?
        let request = NSFetchRequest(entityName: "DataPoint")
        do {
            // Get all data points and return the list size.
            return try context.executeFetchRequest(request).count
        } catch _ as NSError {
            // TODO: Log error?
            print("Failed to get and count all DataPoints.")
            return 0
        }
    }
    
    // Returns all data as a single newline-delimited string. Each line of the string is a single space-delimited point containing 7 items: timestamp, accx/y/z, rotx/y/z.
    public func getAllDataAsString() -> String {
        var dataString = ""
        let request = NSFetchRequest(entityName: "DataPoint")
        do {
            // Get all data points, and add each one to the string.
            let listOfDataPoints = try context.executeFetchRequest(request)
            for point: AnyObject in listOfDataPoints {
                let dataPoint = point as! DataPoint
                // convert timestamp into miliseconds since epoch (returns value as double w/ fraction)
                let timestamp = Int64(dataPoint.time.timeIntervalSince1970 * 1000)
                dataString += "\(timestamp) "
                dataString += "\(dataPoint.accx) "
                dataString += "\(dataPoint.accy) "
                dataString += "\(dataPoint.accz) "
                dataString += "\(dataPoint.rotx) "
                dataString += "\(dataPoint.roty) "
                dataString += "\(dataPoint.rotz) "
                dataString += "\(dataPoint.compass_x) "
                dataString += "\(dataPoint.compass_y) "
                dataString += "\(dataPoint.compass_z)\n"
                if dataPoint.loc_changed {
                    dataString += "+ \(dataPoint.loc_alt) \(dataPoint.loc_flr) \(dataPoint.loc_lat) \(dataPoint.loc_lon)\n"
                }
            }
        } catch _ as NSError {
            // TODO: Log error?
            print("Failed to delete all DataPoints.")
            dataString = "Failed. Could not get any datapoints."
        }
        return dataString
    }
    
    // Wipes data from the data set.
    public func clearAllData() {
        let request = NSFetchRequest(entityName: "DataPoint")
        do {
            // Get all data points, and delete them one by one.
            let listOfDataPoints = try context.executeFetchRequest(request)
            for point: AnyObject in listOfDataPoints {
                context.deleteObject(point as! NSManagedObject)
            }
        } catch _ as NSError {
            // TODO: Log error?
            print("Failed to delete all DataPoints.")
        }
        print("Cleared")
    }
}