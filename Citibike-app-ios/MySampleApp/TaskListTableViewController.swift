//
//  TaskListTableViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/9/17.
//
//

import Foundation
import UIKit
import Alamofire
import ObjectMapper
import AlamofireObjectMapper
import AWSMobileHubHelper


class Task{
    var tID: Int
    //var publishTime: Date
    var publishTimeS: String
    //var acceptTime: Date
    var acceptTimeS: String
    var vID: Int
    var arrivalTimeS: String
    //var completionTime: Date
    var completionTimeS: String
    var priority: String
    var tType: Int
    var sID: Int
    var bikeNum: Int
    var comment: String
    var orderNum: Int
    var rejTimeS: String
    
    init(tID: Int, publishTimeS: String
        , acceptTimeS: String
        , vID: Int
        , arrivalTimeS: String
        ,  completionTimeS: String
        ,  priority: String
        ,  tType: Int
        ,  sID: Int
        ,  bikeNum: Int
        , comment: String
        , orderNum: Int
        , rejTimeS: String
        ){
        self.tID = tID
        self.publishTimeS = publishTimeS
        self.acceptTimeS = acceptTimeS
        self.vID = vID
        self.arrivalTimeS = arrivalTimeS
        self.completionTimeS = completionTimeS
        self.priority = priority
        self.tType = tType
        self.sID = sID
        self.bikeNum = bikeNum
        self.comment = comment
        self.orderNum = orderNum
        self.rejTimeS = rejTimeS
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        //formatter.timeZone = NSTimeZone(name: "UTC") as TimeZone!
        //self.publishTime = formatter.date(from: publishTimeS)!
        //self.acceptTime = formatter.date(from: acceptTimeS)!
        //self.completionTime = formatter.date(from: completionTimeS)!
        
    }
}
class TaskListTableViewController: UITableViewController {
    
    var userName: String!
    var userID: String!
    var tasks = [Task]()
    var task_dic = Dictionary<Int,Dictionary<String,Any>>()
    var station_dic = Dictionary<Int,Dictionary<String,Any>>()
    var reasoncode_dic = Dictionary<Int,Dictionary<String,Any>>()
    
    var successText = "You are on break! You can finish the break by updating task, click on the break task, and click 'Complete'"
    
    
    @IBOutlet weak var updateStationButton: UIButton!
    @IBOutlet weak var updateTaskButton: UIButton!
    
    
    @IBOutlet weak var updateView: UIView!
    
    @IBOutlet weak var lunchBreakButton: UIButton!
    @IBOutlet weak var shortBreakButton: UIButton!

    @IBOutlet weak var successLabel: UILabel!
    
    override func viewDidLoad() {
        
        super.viewDidLoad()
        
        self.title = "Task List"
        
        updateTaskButton.layer.cornerRadius = updateTaskButton.frame.height / 2.0
        updateStationButton.layer.cornerRadius = updateStationButton.frame.height / 2.0
        
        
        lunchBreakButton.layer.cornerRadius = lunchBreakButton.frame.height / 2.0
        lunchBreakButton.addTarget(self, action: #selector(lunchBreakButtonPressed), for: .touchUpInside)
        lunchBreakButton.frame.origin.x = view.center.x - lunchBreakButton.frame.width / 2.0
        
        shortBreakButton.layer.cornerRadius = shortBreakButton.frame.height / 2.0
        shortBreakButton.addTarget(self, action: #selector(shortBreakButtonPressed), for: .touchUpInside)
        shortBreakButton.frame.origin.x = view.center.x   - shortBreakButton.frame.width / 2.0
        
        
        successLabel.text = ""
        successLabel.frame.origin.x = view.center.x   - successLabel.frame.width / 2.0
        
        let identityManager = AWSIdentityManager.default()
        
        if let identityUserName = identityManager.identityProfile?.userName {
            userName = identityUserName
        } else {
            userName = NSLocalizedString("Guest User", comment: "Placeholder text for the guest user.")
        }
        
        userID = identityManager.identityId
        
        updateTaskButton.addTarget(self, action: #selector(fetchTasks), for: .touchUpInside)
        updateStationButton.addTarget(self, action: #selector(fetchStations), for: .touchUpInside)
        
        if self.station_dic.count == 0 {
            fetchStations()
        }
        
        fetchTasks()
        

        
        
        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem()
        

    }
    
    override func viewWillAppear(_ animated: Bool) {
        do{
            self.fetchTasks()
        }
    }
    
    func fetchTasks(){

        var api = FetchTasksAPI()
        api.fetchTasks(username: userName){
            (tasks: [Task]) in
            self.tasks = tasks
            
            if tasks.count != 0 {
                self.tasks = [tasks[0]]
            }
//            self.tableView.reloadData()
            
            DispatchQueue.main.sync {
                self.tableView.reloadData()

            }
        }
        
        api.fetchTaskTypes(){
            (task_dic: Dictionary<Int,Dictionary<String,Any>>) in
            self.task_dic = task_dic
//            self.tableView.reloadData()
            
            DispatchQueue.main.sync {
                self.tableView.reloadData()
            }
        }
        
        api.fetchReasonCode(){
            (reasoncode_dic: Dictionary<Int,Dictionary<String,Any>>) in
            self.reasoncode_dic = reasoncode_dic
            //            self.tableView.reloadData()
            
            DispatchQueue.main.sync {
                self.tableView.reloadData()
            }
        }

    }
    

    func fetchStations(){
        var api = FetchTasksAPI()
        api.fetchStations(){
            (station_dic: Dictionary<Int,Dictionary<String,Any>>) in
            self.station_dic = station_dic
//            self.tableView.reloadData()
            
            DispatchQueue.main.sync {
                self.tableView.reloadData()

            }
            
        }

    }
    
    
    func lunchBreakButtonPressed(){
        
        var contents = ""
        let url = URL(string: "http://ec2-54-196-202-203.compute-1.amazonaws.com/assignBreak?vID=\(vID)&tType=16&dID1=\(dID1)&dID2=\(dID2)&aclati=\(vlatitude)&aclongi=\(vlongitude)")!
        successLabel.text = "Sorry there is a problem."
        
        do{
            contents = try String(contentsOf: url)
            
        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
            
        }
        
        if contents.contains("success"){
            //            lunchBreakButton.isEnabled = false
            //            endTime = NSDate.init(timeIntervalSinceNow: (30 * 60.0))
            successLabel.text = successText
            
        }else{
            successLabel.text = contents
        }
    }
    
    func shortBreakButtonPressed(){
        
        var contents = ""
        let url = URL(string: "http://ec2-54-196-202-203.compute-1.amazonaws.com/assignBreak?vID=\(vID)&tType=17&dID1=\(dID1)&dID2=\(dID2)&aclati=\(vlatitude)&aclongi=\(vlongitude)")!
        successLabel.text = "Sorry there is a problem."
        
        do{
            contents = try String(contentsOf: url)
            
        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
            
        }
        
        if contents.contains("success"){
            //            lunchBreakButton.isEnabled = false
            //            endTime = NSDate.init(timeIntervalSinceNow: (30 * 60.0))
            successLabel.text = successText
            
        }else{
            successLabel.text = contents
        }
    }
    


    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    // MARK: - Table view data source

    override func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 1
    }

    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // #warning Incomplete implementation, return the number of rows
        return self.tasks.count
    }


    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cellIdentifier = "taskCell"
        guard let cell = tableView.dequeueReusableCell(withIdentifier: cellIdentifier, for: indexPath) as? TaskTableViewCell  else {
            fatalError("The dequeued cell is not an instance of TaskTableViewCell.")
        }
        //let cell = tableView.dequeueReusableCell(withIdentifier: "reuseIdentifier", for: indexPath)
//        let cell = TaskTableViewCell()
//        //let cell = UITableViewCell(style: .default, reuseIdentifier: "reuseIdentifier")
        
        let task = tasks[indexPath.row]
        cell.TaskIDLabel.text = "Task # \(task.tID)"
        var tName = ""
        var sName = ""
        if let taskType = task_dic[task.tType]{
            tName = taskType["tName"] as! String
        }
        
        if let station = station_dic[task.sID]{
            sName = station["stationName"] as! String}
        cell.TaskDesTextView.text = "\(tName), \(task.bikeNum) bikes at \(sName) by \(task.completionTimeS) "
        cell.TaskDesTextView.isEditable = false
//      cell.textLabel?.text = task.name

        return cell
    }


    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let task = tasks[indexPath.row]
        
        let taskViewController = TaskViewController()
        taskViewController.task = task
        taskViewController.task_dic = self.task_dic
        taskViewController.station_dic = self.station_dic
        taskViewController.reasoncode_dic = self.reasoncode_dic
        navigationController?.pushViewController(taskViewController, animated: true)
    }

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
    */

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCellEditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
