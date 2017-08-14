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
    
    
    
    let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getVehicles.json"

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
    
    func getListFromData(data: Data) -> [Dictionary<String,Any>]? {
        
        if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: .allowFragments) {
            if let jsonList = jsonObject as? [Dictionary<String,Any>]{
                
                return jsonList
            }
        }
        
        return nil
    }
    

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

