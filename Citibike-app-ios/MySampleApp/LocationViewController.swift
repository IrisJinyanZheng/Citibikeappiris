//
//  LocationViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/28/17.
//
//


import UIKit
import CoreLocation

var vlatitude = ""
var vlongitude = ""

class LocationViewController: UIViewController, CLLocationManagerDelegate {
    var latitude: UILabel!
    var longitude: UILabel!
    var horizontalAccuracy: UILabel!
    var altitude: UILabel!
    var verticalAccuracy: UILabel!
    var distance: UILabel!
    
    var locationManager: CLLocationManager = CLLocationManager()
    var startLocation: CLLocation!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        view.backgroundColor = .white
        
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
        startLocation = nil
        
        setupView()
        
        // Do any additional setup after loading the view.
    }
    
    func setupView(){
        let labelLeftEdgeInset: CGFloat = 20
        let textFieldTopInset: CGFloat = 30
        let textFieldHeight: CGFloat = 40
        let textFieldSeparator: CGFloat = 10
        let textFieldLabelWidth = view.frame.width * 0.5 - labelLeftEdgeInset
        let textFieldWidth = view.frame.width * 0.5 - labelLeftEdgeInset
        
        
        latitude = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: textFieldTopInset, width: textFieldLabelWidth, height: textFieldHeight))
        longitude = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: latitude.frame.origin.y + latitude.frame.height + textFieldSeparator, width: textFieldLabelWidth, height: textFieldHeight))
        horizontalAccuracy = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: longitude.frame.origin.y + longitude.frame.height + textFieldSeparator, width: textFieldLabelWidth, height: textFieldHeight))
        
        
        view.addSubview(latitude)
        view.addSubview(longitude)
        view.addSubview(horizontalAccuracy)
        //   view.addSubview(altitude)
        
        
    }
    
    func resetDistance(_ sender: AnyObject) {
        startLocation = nil
    }
    
    func locationManager(_ manager: CLLocationManager,
                         didUpdateLocations locations: [CLLocation])
    {
        let latestLocation: CLLocation = locations[locations.count - 1]
        
        latitude.text = String(format: "%.4f",
                               latestLocation.coordinate.latitude)
        
        longitude.text = String(format: "%.4f",
                                latestLocation.coordinate.longitude)
        vlatitude = latitude.text!
        vlongitude = longitude.text!
        
        horizontalAccuracy.text = String(format: "%.4f",
                                         latestLocation.horizontalAccuracy)
        //      altitude.text = String(format: "%.4f",
        //                            latestLocation.altitude)
        //      verticalAccuracy.text = String(format: "%.4f",
        //                                    latestLocation.verticalAccuracy)
        
        if startLocation == nil {
            startLocation = latestLocation
        }
        
        let distanceBetween: CLLocationDistance =
            latestLocation.distance(from: startLocation)
        
        //       distance.text = String(format: "%.2f", distanceBetween)
    }
    
    func locationManager(_ manager: CLLocationManager,
                         didFailWithError error: Error) {
        
    }
    
    
    
}
