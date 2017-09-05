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
    /** json of Tasks **/
    let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getTasks.json"
    /** json of TaskTypes **/
    let link2 = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getTaskTypes.json"
    /** json of stations **/
    let link3 = "http://ec2-54-196-202-203.compute-1.amazonaws.com/getStations.json"
    let link4 = link_base + "/reasonCode.json"
    
    /** This method is called in viewcontroller. It transforms the raw json data into a more efficient data structure. reasoncode_dic, passed as parameter of completion handler, is stored in the model of viewcontroller where reasoncode_dic[reasonID] returns all information associated with that particular reasonID **/
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
    /** create a datastructure reasoncode_dic where reasoncode_dic[reasonID] returns the all the information associated with this reasonID **/
    func getReasonCodeFromJSON(json: [Dictionary<String,Any>]) -> Dictionary<Int, Dictionary<String, Any>>{
        var reasoncode_dic = Dictionary<Int, Dictionary<String, Any>>()
        
        for reasoncode in json {
            
            if let rID = reasoncode["reasonID"] as? Int{
                    
                    reasoncode_dic[rID] = reasoncode
                
            }
        }
        
        return reasoncode_dic
    }
    
    /** transform the raw json data into an array of Tasks used to populate tableview.
     All the Tasks in the array have username specificed in parameter **/
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
    
    /** This method is called in viewcontroller. It transforms the raw json data into a more efficient datastructure task_dic. task_dic[taskID] stores all information related to the particular taskID **/
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
    /** This method is called in viewcontroller. It transforms the raw json data into a more efficient datastructure station_dic. station_dic[stationID] stores all information related to the particular stationID **/

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
    /** Helper method used in fetchReasonCode and fetchStations. transform the raw data into type of Dictionary<String,Any> to be more easily parsed **/
    func getListFromData(data: Data) -> [Dictionary<String,Any>]? {
        
        if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: .allowFragments) {
            if let jsonList = jsonObject as? [Dictionary<String,Any>]{
                
                return jsonList
            }
        }
        
        return nil
    }
    
    /** Parse the raw data into a dictionary of type Dictionary<String,Dictionary<String,Any>>**/
    func getDictionaryFromData(data: Data) -> Dictionary<String, Dictionary<String, Any>>? {
        
        if let jsonObject = try? JSONSerialization.jsonObject(with: data, options: .allowFragments) {
            if let jsonDictionary = jsonObject as? Dictionary<String, Dictionary<String, Any>>{
                return jsonDictionary
            }
        }
    
        return nil
    }
    /** the first parameter is the json data processed by method getListFromData.
        It returns a more efficient datastructure station_dic where station_dic[stationID] stores all information related to that particular station_ID**/
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
    
    
    /** the first parameter is the json data processed by method getListFromData.
     It returns a more efficient datastructure task_dic where task_dic[tType] stores all information related to that particular tType **/
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
    
    /** parse the json dictionary into Task objects which can be used to populate tableview cells **/
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

