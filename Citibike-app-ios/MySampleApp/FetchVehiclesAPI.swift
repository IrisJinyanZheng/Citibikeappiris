//
//  FetchVehiclesAPI.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/28/17.
//
//

import Foundation
import UIKit
import Alamofire
import AWSMobileHubHelper

class FetchVehiclesAPI{
    
    
    /** json of the vehicle information **/
    let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getVehicles.json"
    /**create a list of all the vehicleID contained in json**/
    func fetchVehiclesList(completion:@escaping ([Int]) -> ()){
        
        guard let url = URL(string: link) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    var vehicleList = [Int]()
                    
                    for v in json {
                        if v["vID"] as! Int != -111{
                        vehicleList.append(v["vID"] as! Int)

                        }
                    }

                    completion(vehicleList)
                }
            }
            
        }
        
        task.resume()
        
    }

    /**This method is called in view controller. It transforms the raw json into a more efficient data structure. vehicle_dic[vehicleID] returns all information associated with this vehicle. Then vehicle_dic is passed as parameter into completion handler to be used in view controller**/
    func fetchVehicles(completion:@escaping (Dictionary<Int, Dictionary<String, Any>>) -> ()){
        
        guard let url = URL(string: link) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    
                    let vehicle_dic = self.getVehiclesFromJSON(json: json)
                    completion(vehicle_dic)
                }
            }
            
        }
        
        task.resume()
        
    }
    /** Helper method. transform the raw data to a Dictionary more easily parsed  **/
    func getListFromData(data: Data) -> [Dictionary<String,Any>]? {
        
        if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: .allowFragments) {
            if let jsonList = jsonObject as? [Dictionary<String,Any>]{
                
                return jsonList
            }
        }
        
        return nil
    }
    
   /**transform the raw json into a more efficient data structure. vehicle_dic[vehicleID] returns all information associated with this vehicle **/
    func getVehiclesFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<Int, Dictionary<String, Any>>{
        var vehicle_dic = Dictionary<Int, Dictionary<String, Any>>()
        
        for vehicle in json {
            
            if let vID = vehicle["vID"] as? Int{
                
                if vID != -111 {
                    
                vehicle_dic[vID] = vehicle
                }
            }
        }
        
        return vehicle_dic
    }

    
    
}

