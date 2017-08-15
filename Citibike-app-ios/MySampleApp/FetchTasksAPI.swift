//
//  FetchTasksAPI.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/9/17.
//
//

import Foundation
import UIKit
import Alamofire
import AWSMobileHubHelper

let link_base = "http://ec2-54-196-202-203.compute-1.amazonaws.com"

class FetchTasksAPI{
    
    let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getTasks.json"
    let link2 = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getTaskTypes.json"
    let link3 = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getStations.json"
    let link4 = link_base + "/reasonCode.json"
    
    
    func fetchReasonCode(completion:@escaping (Dictionary<Int, Dictionary<String, Any>>) -> ()){
        
        guard let url = URL(string: link4) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    
                    let reasoncode_dic = self.getReasonCodeFromJSON(json: json)
                    completion(reasoncode_dic)
                }
            }
            
        }
        
        task.resume()
        
    }
    
    func getReasonCodeFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<Int, Dictionary<String, Any>>{
        var reasoncode_dic = Dictionary<Int, Dictionary<String, Any>>()
        
        for reasoncode in json {
            
            if let rID = reasoncode["reasonID"] as? Int{
                    
                    reasoncode_dic[rID] = reasoncode
                
            }
        }
        
        return reasoncode_dic
    }
    

    func fetchTasks(username: String, completion:@escaping ([Task]) -> ()){
        
        guard let url = URL(string: link) else {return}
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let dictionary = self.getDictionaryFromData(data: unwrappedData){
                    let task = self.getTasksFromJSON(json: dictionary, username: username)
                    completion(task)
                }
            }
            
        }
        
        task.resume()
    }
    
    
    func fetchTaskTypes(completion:@escaping (Dictionary<Int, Dictionary<String,Any>>) -> ()){
        
        guard let url = URL(string: link2) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    
                    let task_dic = self.getTaskTypesFromJSON(json: json)
                    completion(task_dic)
                }
            }
            
        }
        
        task.resume()
   
    }
    
    func fetchStations(completion:@escaping (Dictionary<Int, Dictionary<String, Any>>) -> ()){
        
        guard let url = URL(string: link3) else{return }
        
        let task = URLSession.shared.dataTask(with: url){
            (data: Data?, response: URLResponse?, error: Error?) in
            if let error = error {
                print(error.localizedDescription)
                return
            }
            
            if let unwrappedData = data {
                if let json = self.getListFromData(data: unwrappedData){
                    
                    let station_dic = self.getStationsFromJSON(json: json)
                    completion(station_dic)
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
    
    
    func getDictionaryFromData(data: Data) -> Dictionary<String, Dictionary<String, Any>>? {
        
        if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: .allowFragments) {
            if let jsonDictionary = jsonObject as? Dictionary<String, Dictionary<String, Any>>{
                return jsonDictionary
            }
        }
    
        return nil
    }
    
    func getStationsFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<Int, Dictionary<String, Any>>{
        var station_dic = Dictionary<Int, Dictionary<String, Any>>()
        
        for station in json {
            
            if let sID = station["sID"] as? Int
//                let stationName = station["stationName"] as? String,
//                let latitude = station["latitude"] as? String,
//            let longitude = station["longitude"] as? String,
//                let stAddress1 = station["stAddress1"] as? String
                {
                
                station_dic[sID] = station
                
            }
        }
        
        return station_dic
    }
    
    
    
    func getTaskTypesFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<Int, Dictionary<String,Any>>{
        var task_dic = Dictionary<Int, Dictionary<String,Any>>()
        
        for taskType in json {
            
            if let tType = taskType["tType"] as? Int,
                let tName = taskType["tName"] as? String,
                let deltaBike = taskType["deltaBike"] as? Int{
                
              //  task_dic[tType] = tName
                task_dic[tType] = taskType
                
            }
        }
        
        return task_dic
    }
    
    
    func getTasksFromJSON(json: Dictionary<String, Dictionary<String, Any>>, username:String) -> [Task]{
        
        var tasks = [Task]()
        for (_,value) in json {
            vID = getvID()
            if "\(value["vID"])" == "Optional(\(vID))" {

                if let publishTimeS = value["publishTime"] as? String,
                            let tID = value["tID"] as? Int,
                            let vID = value["vID"] as? Int,
                            let tType = value["tType"] as? Int,
                            let sID = value["sID"] as? Int,
                            let bikeNum = value["bikeNum"] as? Int,
                            let orderNum = value["orderNum"] as? Int{
                    
                    let completionTimeS = ""
                    let acceptTimeS = ""
                    let rejTimeS = ""
                    let comment = ""
                    let task = Task(tID: tID, publishTimeS: publishTimeS, acceptTimeS: acceptTimeS, vID: vID, arrivalTimeS: "", completionTimeS: completionTimeS, priority: String(1), tType: tType, sID: sID, bikeNum: bikeNum, comment: comment, orderNum: orderNum, rejTimeS: rejTimeS)

                    
                    if let acceptTimeS = value["acceptTime"] as? String
                        {
                            task.acceptTimeS = acceptTimeS
                        }
                    if let arrivalTimeS = value["arrivalTime"] as? String
                    {
                        task.arrivalTimeS = arrivalTimeS
                    }
                    if let completionTimeS = value["completionTime"] as? String
                    {
                        task.completionTimeS = completionTimeS
                    }
                    if let priority = value["priority"] as? String
                    {
                        task.priority = priority
                    }
                    if let rejTimeS = value["rejTime"] as? String
                    {
                        task.rejTimeS = rejTimeS
                    }
                    if let commentS = value["comment"] as? String
                    {
                        task.comment = commentS
                    }
                    
                    tasks.append(task)
                }
            }
        }
        

        tasks.sort(by: {$0.orderNum < $1.orderNum})
        
        return tasks
    }
    

}

