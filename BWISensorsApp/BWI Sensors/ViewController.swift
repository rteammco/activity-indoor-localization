//
//  ViewController.swift
//  BWI Sensors
//
//  Created by Richard Teammco on 10/8/15.
//  Copyright © 2015 Richard Teammco. All rights reserved.
//

import CoreLocation
import CoreMotion
import Foundation
import MessageUI
import SystemConfiguration.CaptiveNetwork
import UIKit

class ViewController: UIViewController, CLLocationManagerDelegate, MFMailComposeViewControllerDelegate {

    @IBOutlet weak var accX: UILabel!
    @IBOutlet weak var accY: UILabel!
    @IBOutlet weak var accZ: UILabel!
    
    @IBOutlet weak var rotX: UILabel!
    @IBOutlet weak var rotY: UILabel!
    @IBOutlet weak var rotZ: UILabel!
    
    @IBOutlet weak var locationLabel: UILabel!
    @IBOutlet weak var locationAccuracyLabel: UILabel!
    @IBOutlet weak var otherLocInfoLabel: UILabel!
    
    @IBOutlet weak var compassLabel: UILabel!
    
    @IBOutlet weak var bssidLabel: UILabel!
    
    @IBOutlet weak var loggingSwitch: UISwitch!
    @IBOutlet weak var logRateSlider: UISlider!
    @IBOutlet weak var numPointsSavedLabel: UILabel!
    @IBOutlet weak var logRateLabel: UILabel!
    
    var motionManager: CMMotionManager!
    var locationManager: CLLocationManager!
    var dataManager: DataManager!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        
        // Initialize variables.
        motionManager = CMMotionManager()
        locationManager = CLLocationManager()
        dataManager = DataManager()
        
        // Update log rate slider to the current value (number of samples per second).
        logRateSlider.minimumValue = 1
        logRateSlider.maximumValue = 30
        let samplesPerSecond = dataManager.getSamplesPerSecond()
        logRateSlider.value = Float(samplesPerSecond)
        logRateLabel.text = "Log Rate: \(samplesPerSecond) / sec"
        
        // Update UI with number of data points saved.
        updateDataPointCount()
        
        // Start updating.
        startMotionUpdates()
        startLocationManager()
        
        getWiFiAPInfo()
    }
    
    // Set up and start accelerometer and gyro readings. The interval indicates the motion logging rate (how many seconds between each update).
    private func startMotionUpdates() {
        setMotionDataRate(dataManager.getSamplesPerSecond())
        // Start data recording from motion manager.
        motionManager.startAccelerometerUpdatesToQueue(NSOperationQueue.currentQueue()!, withHandler: {
            (accelerometerData, error) in self.updateAccelerometerData(accelerometerData!.acceleration)
            if (error != nil) {
                print("\(error)")
            }
        })
        // Start data recording from motion manager.
        motionManager.startGyroUpdatesToQueue(NSOperationQueue.currentQueue()!, withHandler: {
            (gyroData, error) in self.updateGyroData(gyroData!.rotationRate)
            if (error != nil) {
                print("\(error)")
            }
        })
    }
    
    // Updates the motion manager's data sampling interval for both accelerometer and gyroscope.
    private func setMotionDataRate(samplesPerSecond: Int32) {
        let interval = 1.0 / Double(samplesPerSecond)
        motionManager.accelerometerUpdateInterval = interval
        motionManager.gyroUpdateInterval = interval
    }
    
    // Set up and start location manager.
    private func startLocationManager() {
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestAlwaysAuthorization()
        locationManager.startUpdatingLocation()
        if (!CLLocationManager.headingAvailable()) {
            showAlertMessage("Heading not available", message: "Compass heading is not available right now.")
        } else {
            locationManager.startUpdatingHeading()
        }
    }
    
    // Updates the text label to display the number of points that were saved.
    private func updateDataPointCount() {
        numPointsSavedLabel.text = "\(dataManager.numberOfPoints()) Points Saved"
    }
    
    // Gets the BSSID / Mac address of the connected WiFi access point.
    // PROBLEM: This is deprecated and supposedly doesn't work in iOS 9.
    private func getWiFiAPInfo() {
//        let myArray = CNCopySupportedInterfaces()
//        if myArray == nil {
//            bssidLabel.text = "BSSID: #sorrynotsorry #1"
//            return
//        }
//        let infoStringUnsafePointer = CFArrayGetValueAtIndex(myArray!, 0)
//        print(infoStringUnsafePointer)
//        print("-------------")
//        let omg = UnsafePointer<CChar>(infoStringUnsafePointer)
//        var infoString = ""
//        while omg.memory != 0 {
//            infoString += "\(omg.memory)"
//            omg.advancedBy(1)
//        }
//        //return
//        //let infoString = infoStringUnsafePointer as! CFString
//        print(infoString)
//        print("-------------")
//        return
//        let captiveNetwork = CNCopyCurrentNetworkInfo(infoString)
//        if captiveNetwork == nil {
//            bssidLabel.text = "BSSID: #sorrynotsorry #2"
//            return
//        }
//        let bssidUnsafePointer = CFDictionaryGetValue(captiveNetwork, "BSSID")
//        if bssidUnsafePointer == nil {
//            bssidLabel.text = "BSSID: #sorrynotsorry #3"
//        } else {
//            let bssid = bssidUnsafePointer as! CFString
//            bssidLabel.text = "BSSID: \(bssid)"
//        }
        //print(bssid)
    }
    
    // Toggle logging on and off.
    @IBAction func toggleLogging(sender: AnyObject) {
        dataManager.setLoggingState(loggingSwitch.on)
        updateDataPointCount()
    }
    
    // When the slider changes, update the sample rate to that amount.
    @IBAction func updateSampleRate(sender: AnyObject) {
        // Update the displayed value and save it to DataManager.
        let timesPerSecond = Int32(logRateSlider.value)
        dataManager.setSamplesPerSecond(timesPerSecond)
        logRateLabel.text = "Log Rate: \(timesPerSecond) / sec"
        // Update the motion timers as well.
        setMotionDataRate(timesPerSecond)
    }
    
    // Exports data (using email for now). The samples per second are recorded as whatever the latest value is. The user must be careful not to mix sample rates.
    @IBAction func exportAllData(sender: AnyObject) {
        let mailComposeViewController = MFMailComposeViewController()
        mailComposeViewController.mailComposeDelegate = self
        mailComposeViewController.setSubject("Your motion data")
        let mailMessage = "timestamp accx accy accz rotx roty rotz headx heady headz\n+ alt flr lat lon\n\(dataManager.getSamplesPerSecond()) samples per second\n\n" + dataManager.getAllDataAsString()
        mailComposeViewController.setMessageBody(mailMessage, isHTML: false)
        if MFMailComposeViewController.canSendMail() {
            self.presentViewController(mailComposeViewController, animated: true, completion: nil)
        } else {
            showAlertMessage("Could not send mail", message: "Your device apparently fails at sending emails.")
        }
    }
    
    // Wipe all data.
    @IBAction func clearAllData(sender: AnyObject) {
        dataManager.clearAllData()
        updateDataPointCount()
    }
    
    // Updates the accelerometer data values and updates the labels.
    func updateAccelerometerData(acceleration: CMAcceleration) {
        let scale = Double(1000)
        let x = Double(round(scale * acceleration.x) / scale)
        let y = Double(round(scale * acceleration.y) / scale)
        let z = Double(round(scale * acceleration.z) / scale)
        accX.text = "\(x)"
        accY.text = "\(y)"
        accZ.text = "\(z)"
        dataManager.setAccPoint(x, accy: y, accz: z)
    }
    
    // Updates the gyro data values and updates the labels.
    func updateGyroData(rotation: CMRotationRate) {
        let scale = Double(1000)
        let x = Double(round(scale * rotation.x) / scale)
        let y = Double(round(scale * rotation.y) / scale)
        let z = Double(round(scale * rotation.z) / scale)
        rotX.text = "\(x)"
        rotY.text = "\(y)"
        rotZ.text = "\(z)"
        dataManager.setRotPoint(x, roty: y, rotz: z)
    }
    
    // Displays an alert message on the window with "Okay" as the only option.
    func showAlertMessage(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: UIAlertControllerStyle.Alert)
        alert.addAction(UIAlertAction(title: "Okay", style: UIAlertActionStyle.Default, handler: nil))
        self.presentViewController(alert, animated: true, completion: nil)
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    //*** CLLocationManagerDelegate ***/
    
    // This gets called when the LocationManager fails. This generally happens when there is no location data available.
    func locationManager(manager: CLLocationManager, didFailWithError error: NSError) {
        print("Location Manager Failed \(error.description)")
        locationLabel.text = "Location Manager Failed"
        locationLabel.textColor = UIColor.redColor()
    }
    
    // Updates the location using the location services manager. Displays the data on screen and saves it to the data manager.
    func locationManager(manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        let location = locations.last
        let lat = location!.coordinate.latitude
        let lon = location!.coordinate.longitude
        locationLabel.text = "\(lat), \(lon)"
        let hAccuracy = location!.horizontalAccuracy
        //let vAccuracy = location!.verticalAccuracy
        locationAccuracyLabel.text = "+/- \(hAccuracy) m"
        //print(location)
        let altitude = round(location!.altitude * 1000) / 1000
        var floor = location?.floor?.level
        if (floor == nil) {
            floor = -1
        }
        let movCourse = location!.course.description
        let movSpeed = location!.speed.description
        otherLocInfoLabel.text = "Alt/Fl: \(altitude)/\(floor!), Mov/spd: \(movCourse)/\(movSpeed)"
        // also contains:
        //  estimate of the building floor (.floor)
        //  speed of movement (.speed)
        //  course of movement (.course)
        //  altitude (.altitude)
        //  altitude accuracy estimate (.verticalAccuracy)
        dataManager.setLocValues(lat, lon: lon, alt: altitude, flr: floor!)
    }
    
    // Updates the compass values using the location services manager.
    func locationManager(manager: CLLocationManager, didUpdateHeading heading: CLHeading) {
        let headingX = heading.x as Double
        let headingY = heading.y as Double
        let headingZ = heading.z as Double
        let x = round(headingX * 1000) / 1000
        let y = round(headingY * 1000) / 1000
        let z = round(headingZ * 1000) / 1000
        compassLabel.text = "Compass: \(x), \(y), \(z)"
        dataManager.setCompassValues(headingX, y: headingY, z: headingZ)
    }
    
    //*** MFMailComposeViewControllerDelegate ***/
    
    // When the ComposeMailController" is dismissed, return to the original app view.
    func mailComposeController(controller: MFMailComposeViewController, didFinishWithResult result: MFMailComposeResult, error: NSError?) {
        controller.dismissViewControllerAnimated(true, completion: nil)
    }

}

