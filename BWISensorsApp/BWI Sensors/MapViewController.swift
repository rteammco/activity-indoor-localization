//
//  MapViewController.swift
//  BWI Sensors
//
//  Created by Richard Teammco on 11/9/15.
//  Copyright © 2015 Richard Teammco. All rights reserved.
//

import CoreLocation
import MapKit
import UIKit

class MapViewController: UIViewController, CLLocationManagerDelegate {
    
    @IBOutlet weak var mapView: MKMapView!
    
    var locationManager: CLLocationManager!
    
    var pinDrop: MKPointAnnotation!
    
    var wasCentered: Bool!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Start location manager.
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.requestAlwaysAuthorization()
        locationManager.startUpdatingLocation()
        
        // Set the "your location" pin
        pinDrop = MKPointAnnotation()
        pinDrop.title = "Your Location"
        mapView.addAnnotation(pinDrop)
        
        wasCentered = false;
    }
    
    // Segue back to the previous view that created this view.
    @IBAction func goBackToLastView(sender: AnyObject) {
        self.dismissViewControllerAnimated(true, completion: {});
    }
    
    //*** CLLocationManagerDelegate ***/
    func locationManager(manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        let location = locations.last
        
        // Center the map on the coordinate found by location services.
        let center = CLLocationCoordinate2D(latitude: location!.coordinate.latitude, longitude: location!.coordinate.longitude)
        if !wasCentered {
            let region = MKCoordinateRegion(center: center, span: MKCoordinateSpan(latitudeDelta: 0.001, longitudeDelta: 0.001))
            mapView.setRegion(region, animated: false)
            wasCentered = true
        }
        
        // Show a pin at that location.
        pinDrop.coordinate = center
        
        //let coordinateRegion = MKCoordinateRegionMakeWithDistance(location.coordinate, 2000, 2000)
        //mapView.setRegion(coordinateRegion, animated: true)
    }
}