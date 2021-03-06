//
//  ShiftViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 8/8/17.
//
//

import UIKit

var commonaddress = "http://ec2-54-196-202-203.compute-1.amazonaws.com"

class ShiftViewController: UIViewController {
    
    @IBOutlet weak var notSignInLabel: UILabel!
    
    @IBOutlet weak var vehicle1Label: UILabel!
    @IBOutlet weak var vehicleLabel: UILabel!
    /** pressed when the vehicle info is updated **/
    @IBOutlet weak var vehicleStartButton: UIButton!
    /** displays the start time of label **/
    @IBOutlet weak var vehicleStartLabel: UILabel!
    /** pressed when the both drivers have ended shift **/
    @IBOutlet weak var vehicleEndButton: UIButton!
    
    @IBOutlet weak var driver1Label: UILabel!
    /** pressed when driver1 starts shift **/
    @IBOutlet weak var driver1StartButton: UIButton!
    /** pressed when driver1 ends shift **/
    @IBOutlet weak var driver1EndButton: UIButton!
    /** shows the start time of driver1**/
    @IBOutlet weak var driver1StartLabel: UILabel!
    /** shows the end time of driver1**/
    @IBOutlet weak var driver1EndLabel: UILabel!
    /** displays "waiting" if vehicle info hasn't been updated **/
    @IBOutlet weak var driver1PendingLabel: UILabel!
    
    @IBOutlet weak var driver2Label: UILabel!
    @IBOutlet weak var driver2StartButton: UIButton!
    @IBOutlet weak var driver2EndButton: UIButton!
    @IBOutlet weak var driver2StartLabel: UILabel!
    @IBOutlet weak var driver2EndLabel: UILabel!
    @IBOutlet weak var driver2PendingLabel: UILabel!
    /** set the view to default and refresh vehicle & shift data **/
    @IBOutlet weak var refreshButton: UIButton!
    
    /** shift_dic is a more efficient data structure than the original json.
     e.g. If driverID = 250, then shift_dic[250] returns the information associated with this driverID, which is of type Dic<String,Any>
     **/
    var shift_dic = Dictionary<String,Dictionary<String,Any>>()
    
    /** vehicle_dic is a more efficient data structure than the original json.
     e.g. If viehcleID = 250, then vehicle_dic[250] returns the information associated with this viehcleID, which is of type Dic<String,Any>
     **/
    var vehicle_dic = Dictionary<Int,Dictionary<String,Any>>()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
//        vID = 13
//        dID1 = "aa123"
//        dID2 = "ff123"
   
        if (vID==0 ){
            //|| dID1=="" || dID2==""
//            don't display the labels if has not updated vehicle info
            vehicleStartLabel.isHidden = true
            driver1StartLabel.isHidden = true
            driver1EndLabel.isHidden = true
            driver1PendingLabel.isHidden = true
            driver2StartLabel.isHidden = true
            driver2EndLabel.isHidden = true
            driver2PendingLabel.isHidden = true
        }else{
            fetchVehicles()
            fetchShifts()
            setupViews()
            refreshButton.isEnabled = true
            refreshButton.addTarget(self, action: #selector(refreshButtonPressed), for: .touchUpInside)
        }
        // Do any additional setup after loading the view.
    }
    /** set the view to default and refresh vehicle & shift data **/
    func refreshButtonPressed(){
        driver1PendingLabel.isHidden = true
        driver1PendingLabel.text = "waiting..."
        driver2PendingLabel.isHidden = true
        driver2PendingLabel.text = "waiting..."
        fetchVehicles()
        fetchShifts()
        setupViews()
    }
    /*set the view to default, then update the view according to vehicle & shift data */
    func setupViews(){
    
        notSignInLabel.isHidden = true
        driver1PendingLabel.isHidden = true
        driver2PendingLabel.isHidden = true
        
        vehicle1Label.text = "Vehicle #\(vID)"
        vehicleLabel.text = "Vehicle #\(vID)"
        driver1Label.text = "\(dID1)"
        driver2Label.text = "\(dID2)"
        
        setupTimeStrings()
        setupButtonTargets()
        
    }
    
    /** add handler methods to UIbuttons **/
    func setupButtonTargets(){
        vehicleStartButton.addTarget(self, action: #selector(vehicleStartButtonPressed), for: .touchUpInside)
        vehicleEndButton.addTarget(self, action: #selector(vehicleEndButtonPressed), for: .touchUpInside)
        driver1StartButton.addTarget(self, action: #selector(driver1StartButtonPressed), for: .touchUpInside)
        driver1EndButton.addTarget(self, action: #selector(driver1EndButtonPressed), for: .touchUpInside)
        driver2StartButton.addTarget(self, action: #selector(driver2StartButtonPressed), for: .touchUpInside)
        driver2EndButton.addTarget(self, action: #selector(driver2EndButtonPressed), for: .touchUpInside)

    }
    /** called when vehicle info is updated **/
    func vehicleStartButtonPressed(){
        vehicleShiftButtonPressed(vID: vID, mode: "start")
        vehicleStartButton.isEnabled = false
    }
    /** called when both drivers have ended their shifts **/
    func vehicleEndButtonPressed(){
        vehicleShiftButtonPressed(vID: vID, mode: "end")
        vehicleEndButton.isEnabled = false
    }
    
    func driver1StartButtonPressed(){
        let contents = driverShiftButtonPressed(dID: dID1, mode: "start")
        driver1StartLabel.text = contents
        driver1StartButton.isEnabled = false
    }
    
    func driver1EndButtonPressed(){
        let contents = driverShiftButtonPressed(dID: dID1, mode: "end")
        driver1EndLabel.text = contents
        driver1PendingLabel.isHidden = false
        driver1EndButton.isEnabled = false
    }
    
    func driver2StartButtonPressed(){
        let contents = driverShiftButtonPressed(dID: dID2, mode: "start")
        driver2StartLabel.text = contents
        driver2StartButton.isEnabled = false
    }
    
    func driver2EndButtonPressed(){
        let contents = driverShiftButtonPressed(dID: dID2, mode: "end")
        driver2EndLabel.text = contents
        driver2PendingLabel.isHidden = false
        driver2EndButton.isEnabled = false
    }
    /** update the label that displays info on shift start time **/
    func vehicleShiftButtonPressed(vID: Int, mode: String){
        var contents = ""
        let link = commonaddress + "/updateVehicleShift/mode=\(mode)&vID=\(vID)"
        
        let url = URL(string: link.addingPercentEncoding( withAllowedCharacters: .urlQueryAllowed)!)!
        
        do{
            contents = try String(contentsOf: url)
        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
        }
        vehicleStartLabel.text = contents
    }
    /** when driver pressed the shift button, update the UI on start time, end time, is waiting etc
     **/
    func driverShiftButtonPressed(dID:String, mode:String) -> String{

        var contents = ""
        let link = commonaddress + "/updateDriversShift/mode=\(mode)&dID=\(dID)&vID=\(vID)"
        
        let url = URL(string: link.addingPercentEncoding( withAllowedCharacters: .urlQueryAllowed)!)!
        
        do{
            contents = try String(contentsOf: url)
        }catch let error as NSError {
            contents = "\(error)"
            print("Error: \(error)")
        }
        return contents
    }

    
    /** Update vehicle start time, driver start time and driver end time.
        Show estimate if he hasn't signed in or signed out.
     **/
    func setupTimeStrings(){
        let shift1 = shift_dic[dID1]
        let shift2 = shift_dic[dID2]
        let v = vehicle_dic[vID]
        
//        update vehicle start time
        if let vStartTime = v?["startTime"] as? String{
            vehicleStartLabel.text = vStartTime
            vehicleEndButton.isEnabled = true //enable vehicle shift start button if has started
            vehicleStartButton.isEnabled = false
        }else{
            vehicleStartButton.isEnabled = true //enable vehicle shift start button if not started yet
            vehicleEndButton.isEnabled = false
        }
        
        
//        update driver start time, show estimate if not signed in yet
        if let d1StartTime = shift1?["signInTimeEstimate"] as? String{
            driver1StartLabel.text = d1StartTime
        }
        if let d1StartTime = shift1?["signInTime"] as? String{
//            won't update if None in database
            driver1StartLabel.text = d1StartTime
            driver1StartButton.isEnabled = false//disable driver shift start button if has started
            driver1EndButton.isEnabled = true
        }else{
            driver1StartButton.isEnabled = true //enable driver shift start button if not started yet
            driver1EndButton.isEnabled = false
        }
        
        if let d2StartTime = shift2?["signInTimeEstimate"] as? String{
            driver2StartLabel.text = d2StartTime
        }
        if let d2StartTime = shift2?["signInTime"] as? String{
            driver2StartLabel.text = d2StartTime
            driver2StartButton.isEnabled = false//disable driver shift start button if has started
            driver2EndButton.isEnabled = true
        }else{
            driver2StartButton.isEnabled = true //enable driver shift start button if not started yet
            driver2EndButton.isEnabled = false
        }
        
//        update driver end time, show estimate if not request sign out yet
        if let d1EndTime = shift1?["signOutTimeEstimate"] as? String{
            driver1EndLabel.text = d1EndTime
        }
        if let d1EndTime = shift1?["signOutReqTime"] as? String{
            driver1EndLabel.text = d1EndTime
            driver1EndButton.isEnabled = false
            driver1PendingLabel.isHidden = false
        }
        
        if let d2EndTime = shift2?["signOutTimeEstimate"] as? String{
            driver2EndLabel.text = d2EndTime
        }
        if let d2EndTime = shift2?["signOutReqTime"] as? String{
            driver2EndLabel.text = d2EndTime
            driver2EndButton.isEnabled = false
            driver2PendingLabel.isHidden = false
        }
        
//        if disproved sign out:
        if let d1Des = shift1?["disproved"] as? Int{
            if (d1Des == 1){
                driver1PendingLabel.text = "disproved"
                driver1PendingLabel.isHidden = false
            }
        }
        if let d2Des = shift2?["disproved"] as? Int{
            if (d2Des == 1){
                driver2PendingLabel.text = "disproved"
                driver2PendingLabel.isHidden = false
            }
        }
    }
    /** update self.shift_dic, where shift_dic[driverID] returns the information associated with this driverID.
        Call setupTimeStrings to display info on time.
     **/
    func fetchShifts(){
        var api = FetchShiftsAPI()
        api.fetchShifts(){
            (shift_dic: Dictionary<String,Dictionary<String,Any>>) in
            self.shift_dic = shift_dic
            DispatchQueue.main.sync {
                self.setupTimeStrings()
            }
        }
    }

    /** update self.vehicle_dic, where vehicle_dic[vehicleID] returns the information associated with this vehicleID.
        Call setupTimeStrings to display info on time.
     **/
    func fetchVehicles(){
        var api = FetchVehiclesAPI()
        api.fetchVehicles(){
            (vehicle_dic: Dictionary<Int,Dictionary<String,Any>>) in
            self.vehicle_dic = vehicle_dic

            DispatchQueue.main.sync {
                self.setupTimeStrings()
            }
        }
    }

    
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    


}
