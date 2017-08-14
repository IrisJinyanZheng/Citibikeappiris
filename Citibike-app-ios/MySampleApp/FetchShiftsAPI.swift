//
//  FetchShiftsAPI.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 8/8/17.
//
//

import Foundation
import UIKit
import Alamofire
import AWSMobileHubHelper

class FetchShiftsAPI{
    
    
    
    let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getShifts.json"
    
    
    func fetchShifts(completion:@escaping (Dictionary<String, Dictionary<String, Any>>) -> ()){
        
        guard let url = URL(string: link) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    
                    let shift_dic = self.getShiftsFromJSON(json: json)
                    completion(shift_dic)
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
    
    
    func getShiftsFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<String, Dictionary<String, Any>>{
        var shift_dic = Dictionary<String, Dictionary<String, Any>>()
        
        for shift in json {
            
            if let dID = shift["dID"] as? String{
                
                if dID != "-111" {
                    
                    shift_dic[dID] = shift
                }
            }
        }
        
        return shift_dic
    }
    
    
    
}

