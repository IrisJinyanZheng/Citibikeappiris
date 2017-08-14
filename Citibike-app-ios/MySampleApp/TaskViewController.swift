//
//  TaskViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/6/17.
//
//

import Foundation
import UIKit
import AWSMobileHubHelper
import Alamofire





class TaskViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource, UITextFieldDelegate {
    //var taskLabel: UILabel!
    
    var rejectReasonID = -1
    var taskInfoTextView: UITextView!

    var taskStatusLabel: UILabel!
    var taskAcceptLabel: UILabel!
    

    var completeButton: UIButton!
    var realBikeTextField: UITextField!
    var realBikeLabel: UILabel!
    
    var rejectReasonTextField: UITextField!
    var rejectReason2TextField: UITextField!
    var rejectButton: UIButton!
    var acceptButton: UIButton!
    var arrivalButton: UIButton!
    var rejectReasonPickerView: UIPickerView!
    
    var userName: String!
    var userID: String!
    var task: Task!
    var task_dic: Dictionary<Int, Dictionary<String,Any>>!
    var station_dic: Dictionary<Int,Dictionary<String,Any>>!
    var reasoncode_dic: Dictionary<Int,Dictionary<String,Any>>!
    



    override func viewDidLoad() {
        
        
        super.viewDidLoad()
        
        self.title = "Task ID # \(task.tID)"
        setupView()
        // Do any additional setup after loading the view.
    }
    
    
    func setupView(){
        
        let labelLeftEdgeInset: CGFloat = 20
        let labelSeparator: CGFloat = 30
        let textFieldTopInset: CGFloat = 30
        let textFieldHeight: CGFloat = 40
        let textFieldSeparator: CGFloat = 10
        let textFieldLabelWidth = view.frame.width * 0.5 - labelLeftEdgeInset
        let textFieldWidth = view.frame.width * 0.5 - labelLeftEdgeInset
        
        
//        taskLabel = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: textFieldTopInset, width: textFieldLabelWidth, height: textFieldHeight))
        
//        taskLabel.text = "Task ID # \(task.tID)"
        
        
        taskInfoTextView = UITextView(frame: CGRect(x: 0, y: 10, width: view.frame.width * 0.9, height: 150))
        taskInfoTextView.center = CGPoint(x: view.center.x, y: taskInfoTextView.center.y)
        taskInfoTextView.isEditable = false
        taskInfoTextView.font = UIFont.systemFont(ofSize: 16)
        taskInfoTextView.textAlignment = .center
        taskInfoTextView.textAlignment = .left
        var tName = ""
        var sName = ""
        tName = task_dic[task.tType]?["tName"] as! String
        if let station = station_dic[task.sID]{
            sName = station["stationName"] as! String}
        taskInfoTextView.text = "Task Type: \(tName) \n Bike number: \(task.bikeNum) \n Station: \(sName) \n Deadline: \(task.completionTimeS) \n Comment: \(task.comment)  \n priority: \(task.priority) \n Accept Time: \(task.acceptTimeS) \n Arrival Time:\(task.arrivalTimeS)"

        taskAcceptLabel = UILabel(frame: CGRect(x: 0, y: taskInfoTextView.center.y+taskInfoTextView.frame.height / 2.0 + textFieldSeparator, width: view.frame.width / 2.0, height: 25))
        taskAcceptLabel.center = CGPoint(x: view.center.x, y: taskAcceptLabel.center.y)
        taskAcceptLabel.text = ""
        taskAcceptLabel.font = UIFont.systemFont(ofSize: 10)
        taskAcceptLabel.textAlignment = .center

        
        taskStatusLabel = UILabel(frame: CGRect(x: 0, y: taskAcceptLabel.frame.origin.y+textFieldSeparator , width: view.frame.width / 1.5, height: 50))
        taskStatusLabel.center = CGPoint(x: view.center.x, y: taskStatusLabel.center.y)
        taskStatusLabel.text = "NOT COMPLETED"
        taskStatusLabel.font = UIFont.systemFont(ofSize: 20)
        taskStatusLabel.textAlignment = .center
        
        acceptButton = UIButton(frame: CGRect(x: view.center.x - view.frame.width / 4.0 - view.frame.width / 8.0, y: taskStatusLabel.frame.origin.y + textFieldSeparator * 4.0, width: 100, height: 40))
        acceptButton.setTitle("Accept", for: .normal)
        acceptButton.layer.cornerRadius = acceptButton.frame.height / 2.0
        acceptButton.backgroundColor = .orange
        acceptButton.setTitleColor(UIColor(red: 0, green: 0.478431, blue: 1, alpha: 1), for: .normal)
        acceptButton.setTitleColor(.lightGray, for: .highlighted)
        acceptButton.setTitleColor(.darkGray, for: .disabled)
        acceptButton.addTarget(self, action: #selector(acceptButtonPressed), for: .touchUpInside)
        acceptButton.isEnabled = false
        
        
        arrivalButton = UIButton(frame: CGRect(x: view.center.x + view.frame.width / 4.0 - view.frame.width / 8.0, y: taskStatusLabel.frame.origin.y + textFieldSeparator * 4.0, width: 100, height: 40))
        arrivalButton.setTitle("Arrive", for: .normal)
        arrivalButton.layer.cornerRadius = arrivalButton.frame.height / 2.0
        arrivalButton.backgroundColor = .orange
        arrivalButton.setTitleColor(UIColor(red: 0, green: 0.478431, blue: 1, alpha: 1), for: .normal)
        arrivalButton.setTitleColor(.lightGray, for: .highlighted)
        arrivalButton.setTitleColor(.darkGray, for: .disabled)
        arrivalButton.addTarget(self, action: #selector(arrivalButtonPressed), for: .touchUpInside)
        arrivalButton.isEnabled = false
        
        rejectReasonTextField = UITextField(frame: CGRect(x: 0, y: acceptButton.frame.origin.y+textFieldSeparator * 9.0, width: 350, height: 50))
        rejectReasonTextField.font = UIFont.systemFont(ofSize: 12)
        rejectReasonTextField.textAlignment = .center
        rejectReasonTextField.layer.borderColor = UIColor.black.cgColor
        rejectReasonTextField.backgroundColor = .lightGray
        rejectReasonTextField.placeholder = "Comment..."
        rejectReasonTextField.delegate = self
        
        rejectButton = UIButton(frame: CGRect(x: view.center.x - view.frame.width / 4.0 - view.frame.width / 8.0, y: rejectReasonTextField.frame.origin.y+rejectReasonTextField.frame.height + textFieldSeparator * 3.0, width: 70, height: 40))
        rejectButton.setTitle("Reject", for: .normal)
        rejectButton.layer.cornerRadius = rejectButton.frame.height / 2.0
        rejectButton.setTitleColor(UIColor(red: 0, green: 0.478431, blue: 1, alpha: 1), for: .normal)
        rejectButton.setTitleColor(.lightGray, for: .highlighted)
        rejectButton.setTitleColor(.lightGray, for: .disabled)
        rejectButton.addTarget(self, action: #selector(rejectButtonPressed), for: .touchUpInside)
        
        completeButton = UIButton(frame: CGRect(x: view.center.x + view.frame.width / 4.0 - view.frame.width / 8.0, y: rejectButton.frame.origin.y, width: 100, height: 40))
        completeButton.setTitle("Complete", for: .normal)
        completeButton.setTitleColor(UIColor(red: 0, green: 0.478431, blue: 1, alpha: 1), for: .normal)
        completeButton.setTitleColor(.lightGray, for: .highlighted)
        completeButton.backgroundColor = .orange
        completeButton.layer.cornerRadius = completeButton.frame.height / 2.0
        completeButton.setTitleColor(.darkGray, for: .disabled)
        completeButton.addTarget(self, action: #selector(completeButtonPressed), for: .touchUpInside)
        
//        only enable the button if the button has not been pressed before
        if (task.acceptTimeS.characters.count == 0 || task.acceptTimeS == "null" || task.acceptTimeS == "None") {
            completeButton.isEnabled = false
            acceptButton.isEnabled = true
            taskStatusLabel.text = "NOT ACCEPTED"}

        
        if (task.arrivalTimeS.characters.count == 0 || task.arrivalTimeS == "null" || task.arrivalTimeS == "None") {
            taskInfoTextView.text = "Task Type: \(tName) \n Bike number: show upon arrival \n Station: \(sName) \n Deadline: \(task.completionTimeS) \n Comment: \(task.comment)  \n priority: \(task.priority) \n Accept Time: \(task.acceptTimeS) \n Arrival Time:\(task.arrivalTimeS)"
            arrivalButton.isEnabled = true}
        
//        can't do any operation if the task is waiting for approval of rejection
        if (task.rejTimeS.characters.count != 0 && task.rejTimeS != "null" && task.rejTimeS != "None") {
            completeButton.isEnabled = false
            acceptButton.isEnabled = false
            rejectButton.isEnabled = false
            arrivalButton.isEnabled = false
            taskStatusLabel.text = "Requested Rejection"}

        
        realBikeTextField = UITextField(frame: CGRect(x: completeButton.frame.origin.x + completeButton.frame.width-10, y: rejectReasonTextField.frame.origin.y+rejectReasonTextField.frame.height + 10, width: 20, height: 20))
        realBikeTextField.font = UIFont.systemFont(ofSize: 12)
        realBikeTextField.textAlignment = .center
        realBikeTextField.layer.borderColor = UIColor.black.cgColor
        realBikeTextField.backgroundColor = .orange
        realBikeTextField.text =  "\(task.bikeNum)"
        
        realBikeLabel = UILabel(frame: CGRect(x: completeButton.frame.origin.x - completeButton.frame.width / 2.0, y: realBikeTextField.frame.origin.y, width: view.frame.width / 2.0, height: 25))
        realBikeLabel.text = "Bike Num"
        realBikeLabel.font = UIFont.systemFont(ofSize: 12)
        realBikeLabel.textAlignment = .center
        
//        view.addSubview(taskLabel)
        
        
        rejectReasonPickerView = UIPickerView(frame: CGRect(x: 0, y: view.frame.height - view.frame.height / 3.0, width: view.frame.width, height: view.frame.height / 3.0))//textFieldHeight
        rejectReasonPickerView.delegate = self
        rejectReasonPickerView.dataSource = self
        rejectReasonPickerView.showsSelectionIndicator = true
        rejectReasonPickerView.isHidden = true
        rejectReasonPickerView.backgroundColor = .white
        
        rejectReason2TextField = UITextField(frame: CGRect(x: 0, y: view.frame.height - 70 - 50, width: 250, height: 50))
        rejectReason2TextField.font = UIFont.systemFont(ofSize: 12)
        rejectReason2TextField.textAlignment = .center
        rejectReason2TextField.layer.borderColor = UIColor.black.cgColor
        rejectReason2TextField.backgroundColor = .lightGray
        rejectReason2TextField.placeholder = "Spefic Reason..."
        rejectReason2TextField.isHidden = true
        
        
        view.addSubview(taskInfoTextView)
        view.addSubview(acceptButton)
        view.addSubview(arrivalButton)
        view.addSubview(rejectButton)
        view.addSubview(completeButton)
        view.addSubview(taskStatusLabel)
        view.addSubview(rejectReasonTextField)
        view.addSubview(rejectReason2TextField)
        view.addSubview(realBikeTextField)
        view.addSubview(realBikeLabel)
        
        view.addSubview(taskAcceptLabel)
        view.addSubview(rejectReasonPickerView)
        view.backgroundColor = .white
        
        
    }
    
    
    
    func acceptButtonPressed(){
        
        var nxlongi = 0.0
        var nxlati = 0.0
        if let station = station_dic[task.sID]{
            nxlongi = station["longitude"] as! Double
            nxlati = station["latitude"] as! Double}
        
        
        var contents = ""
        
        let url = URL(string: "http://ec2-54-196-202-203.compute-1.amazonaws.com/response?tid=\(task.tID)&res=1&reason=accepted&lati=\(vlatitude)&longi=\(vlongitude)&vID=\(vID)&nxs=\(task.sID)&nxlati=\(nxlati)&nxlongi=\(nxlongi)")!
//        var urlRequest = URLRequest(url: url)
//        Alamofire.request("http://ec2-54-196-202-203.compute-1.amazonaws.com/response?tid=\(task.tID)&res=1&reason=accepted", method: .post)
//        print("http://ec2-54-196-202-203.compute-1.amazonaws.com/response?tid=\(task.tID)&res=1&reason=accepted")
        //TaskTextView.text = userName
        do{
            contents = try String(contentsOf: url)
            

        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
        }
        
        taskAcceptLabel.text = "\(contents)"
        
        if contents.contains("Accepted Task"){
            arrivalButton.isEnabled = true
            acceptButton.isEnabled = false
            taskStatusLabel.text = "Not Completed"
        
        }
    }
    
    
    
    func arrivalButtonPressed(){
        
        var nxlongi = 0.0
        var nxlati = 0.0
        if let station = station_dic[task.sID]{
            nxlongi = station["longitude"] as! Double
            nxlati = station["latitude"] as! Double}
        
        var reason = ""
        if let r = rejectReasonTextField.text{
            reason = reason + ", complete comment:" + r
        }
        
        
        var contents = ""
//        arrive?tid=600&lati=40.72&longi=-73.97&vID=11&reason=comment
        
        let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/arrive?tid=\(task.tID)&reason=\(reason)&lati=\(vlatitude)&longi=\(vlongitude)&vID=\(vID)"
        
        let url = URL(string: link.addingPercentEncoding( withAllowedCharacters: .urlQueryAllowed)!)!

        do{
            contents = try String(contentsOf: url)
            
            
        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
        }
        
        taskAcceptLabel.text = "\(contents)"
        
        if contents.contains("Arrived"){
            completeButton.isEnabled = true
            navigationController?.popViewController(animated: true)
//            acceptButton.isEnabled = false
//            taskStatusLabel.text = "Not Completed"
            
        }
    }

    
    
    
    func rejectButtonPressed(){
        
        var reason = ""
        
        var alertmessage = "\(rejectReasonID)"
        if (rejectReasonID == -1){
            alertmessage = alertmessage + "NO REASON"
            if let r = rejectReason2TextField.text{
                reason = ", reject reason: " + r
            }
        }
        
        
        let link = "http://ec2-54-196-202-203.compute-1.amazonaws.com/response?tid=\(task.tID)&res=0&reason=\(task.comment)\(reason)&lati=\(vlatitude)&longi=\(vlongitude)&vID=\(vID)&reasonID=\(rejectReasonID)"

        
        let alert = UIAlertController(title: "Reject Task", message: "Are you sure you want to reject the task with reason \(alertmessage)?", preferredStyle: .alert)
        let clearAction = UIAlertAction(title: "Reject", style: .default) { value in
            //self.reject(reason: reason)
            let url = URL(string: link.addingPercentEncoding( withAllowedCharacters: .urlQueryAllowed)!)!
            do{
                let contents = try String(contentsOf: url)
                print(contents)
                self.navigationController?.popViewController(animated: true)
                
            }catch let error as NSError {
                print("Error: \(error)")
                self.taskAcceptLabel.text = "Error: \(error)"
            }
            
            
        }
        let cancelAction = UIAlertAction(title: "Cancel", style: .default, handler: nil)
        
        alert.addAction(clearAction)
        alert.addAction(cancelAction)
        
        present(alert, animated: true, completion:nil)

    }
    
    func completeButtonPressed(){
        
        var res = 1
        
        let deltaBike: Int = task_dic[task.tType]!["deltaBike"] as! Int
        var deltaBikeTotal = deltaBike * task.bikeNum
        
        let text = realBikeTextField.text
        var reason = ""
        var actBikeNum = task.bikeNum
        
        if let db = Int(text!) {
            // Text field converted to an Int
            
            if (db != task.bikeNum){
                actBikeNum = db
                deltaBikeTotal = db * deltaBike
                res = 2
            }
            
            
        } else {
            // Text field is not an Int
            let alert = UIAlertController(title: "Not Number", message: "The bike number has to be an integer", preferredStyle: .alert)
            let cancelAction = UIAlertAction(title: "OK", style: .default, handler: nil)
            alert.addAction(cancelAction)
            
            present(alert, animated: true, completion:nil)
            
        }
        
        
        vBike = vBike + deltaBikeTotal
        
//        update the number of broken bikes
        if (task.tType == 2 || task.tType == 4){
            vBikeBroken = vBikeBroken + deltaBikeTotal
        }
        
        
        if let r = rejectReasonTextField.text{
            reason = "; complete comment:" + r
        }
        
        let stringUrl = "http://ec2-54-196-202-203.compute-1.amazonaws.com/complete?tid=\(task.tID)&lati=\(vlatitude)&longi=\(vlongitude)&vID=\(vID)&vBike=\(vBike)&vBikeBroken=\(vBikeBroken)&res=\(res)&actBikeNum=\(actBikeNum)&reason=\(task.comment)"+reason

        let url = URL(string: stringUrl.addingPercentEncoding( withAllowedCharacters: .urlQueryAllowed)!)!
        
        do{
            let contents = try String(contentsOf: url)
            print(contents)
            navigationController?.popViewController(animated: true)
            
        }catch let error as NSError {
            print("Error: \(error)")
            taskAcceptLabel.text = "Error: \(error)"
        }
        
        
    }

    
    override func viewWillAppear(_ animated: Bool) {
        
        let identityManager = AWSIdentityManager.default()
        
        if let identityUserName = identityManager.identityProfile?.userName {
            userName = identityUserName
        } else {
            userName = NSLocalizedString("Guest User", comment: "Placeholder text for the guest user.")
        }
        
        userID = identityManager.identityId

    }
//    /////////
    
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return reasoncode_dic.count
    }
    
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        let tempreasonID: Int = Array(reasoncode_dic.keys)[row]
        let v = reasoncode_dic[tempreasonID]
        var reasonName = ""
        var rID = -1
        if let vvName = v?["reasonName"] as? String {
            reasonName = vvName
        }
        if let rrID = v?["reasonID"] as? Int {
            rID = rrID
        }
        
        return "\(rID) \(reasonName) "
        
    }
    
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        
        let temprID: Int = Array(reasoncode_dic.keys)[row]
        let v = reasoncode_dic[temprID]
        var reasonName = ""
        var rID = -1
        if let vvName = v?["reasonName"] as? String {
            reasonName = vvName
        }
        if let rrID = v?["reasonID"] as? Int {
            rID = rrID
        }else{
            reasonName = "there is a problem in selecting reason name"
        }
        
        if (rID == 1){
            rejectReason2TextField.isHidden = false
        }else{
            rejectReason2TextField.isHidden = true
        }
        
        self.rejectReasonTextField.text = "\(rID) \(reasonName)";
        rejectReasonID = rID
        rejectReasonPickerView.isHidden = true;
    }
    
    
    
    func textFieldShouldBeginEditing(_ textField: UITextField) -> Bool {
        rejectReasonPickerView.isHidden = false
        return false
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
