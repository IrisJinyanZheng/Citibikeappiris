//
//  VehicleViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/6/17.
//
//

import UIKit
/** history **/
class Event {
    
    var bikeNum: String
    var vID: String
    var dID1: String
    var dID2: String
    var latitude: String
    var longitude: String
    var vBikeBroken: String
    
    init(number: String, vID: String, dID1: String, dID2: String, vBikeBroken: String) {
        self.bikeNum = number
        self.vID = vID
        self.dID1 = dID1
        self.dID2 = dID2
        self.latitude = vlatitude
        self.longitude = vlongitude
        self.vBikeBroken = vBikeBroken
    }
    
    func description() -> String {
        return "\(bikeNum),\(vBikeBroken) bikes on vehicle \(vID), Dirver \(dID1), \(dID2), at \(latitude), \(longitude)"
    }
    
}

var vID = 0
var vBike = 0
var vBikeBroken = 0
var vName = ""
var dID1 = ""
var dID2 = ""
var eventDescriptions = [String]()
var events = [Event]()

func getvID() -> Int{
    return vID

}

class VehicleViewController: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource,UITextFieldDelegate{
    
    var sendEventButton: UIButton!
    var bikeNumLabel: UILabel!
    var bikeNumTextField: UITextField!
    var brokenbikeNumLabel: UILabel!
    var brokenbikeNumTextField: UITextField!
    var vehicleIdLabel: UILabel!
    var vehicleIdTextField: UITextField!
    var resultLabel: UILabel!
    
    
    var updateHistoryTextView: UITextView!
    var clearTextViewButton: UIButton!
    var currentHistorySegmentControl: UISegmentedControl!
    
    var vehicleLabel: UILabel!
    var vehiclePicker: UIPickerView!
    var vehicle_dic = Dictionary<Int,Dictionary<String,Any>>()
    var vehiclePickerData = [Int]()

    var driverLabel: UILabel!
    var driver1TextField: UITextField!
    var driver2TextField: UITextField!
    
    var checkLocationButton: UIButton!
    
    var tempvID = 0
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        
        fetchVehicles()
        setupViews()
        view.backgroundColor = .white
        // Do any additional setup after loading the view.
    }
    
    func setupViews(){
        
        let labelLeftEdgeInset: CGFloat = 20
        let textFieldTopInset: CGFloat = 30
        let textFieldHeight: CGFloat = 40
        let textFieldSeparator: CGFloat = 10
        let textFieldLabelWidth = view.frame.width * 0.45 - labelLeftEdgeInset
        let textFieldWidth = view.frame.width * 0.55 - labelLeftEdgeInset
        
        bikeNumLabel = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: textFieldTopInset, width: textFieldLabelWidth / 2.0, height: textFieldHeight))
        bikeNumLabel.text = "Bikes"
        bikeNumTextField = UITextField(frame: CGRect(x: bikeNumLabel.frame.origin.x + bikeNumLabel.frame.width, y: bikeNumLabel.frame.origin.y, width: 50, height: textFieldHeight))
        bikeNumTextField.borderStyle = .roundedRect
        bikeNumTextField.text = "\(vBike)"
        
        
        brokenbikeNumLabel = UILabel(frame: CGRect(x: bikeNumTextField.frame.origin.x + bikeNumTextField.frame.width + textFieldSeparator, y: textFieldTopInset, width: textFieldLabelWidth, height: textFieldHeight))
        brokenbikeNumLabel.text = "Broken Bikes"
        brokenbikeNumTextField = UITextField(frame: CGRect(x: brokenbikeNumLabel.frame.origin.x + brokenbikeNumLabel.frame.width, y: brokenbikeNumLabel.frame.origin.y, width: 50, height: textFieldHeight))
        brokenbikeNumTextField.borderStyle = .roundedRect
        brokenbikeNumTextField.text = "\(vBikeBroken)"
        
        vehicleIdLabel = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: bikeNumTextField.frame.origin.y+textFieldSeparator * 6.0, width: textFieldLabelWidth, height: textFieldHeight))
        vehicleIdLabel.text = "Vehicle ID "
        
        vehicleIdTextField = UITextField(frame: CGRect(x: vehicleIdLabel.frame.origin.x + vehicleIdLabel.frame.width, y: vehicleIdLabel.frame.origin.y, width: textFieldWidth, height: textFieldHeight))
        vehicleIdTextField.borderStyle = .roundedRect
        vehicleIdTextField.text = "\(vID)"
        vehicleIdTextField.delegate = self
        
        
        vehiclePicker = UIPickerView(frame: CGRect(x: 0, y: view.frame.height - view.frame.height / 3.0, width: view.frame.width, height: view.frame.height / 3.0))//textFieldHeight
        vehiclePicker.delegate = self
        vehiclePicker.dataSource = self
        vehiclePicker.showsSelectionIndicator = true
        vehiclePicker.isHidden = true
        
        driverLabel = UILabel(frame: CGRect(x: labelLeftEdgeInset, y: vehicleIdLabel.frame.origin.y+textFieldSeparator * 6.0, width: textFieldLabelWidth, height: textFieldHeight))
        driverLabel.text = "Drivers' ID's "
        
        driver1TextField = UITextField(frame: CGRect(x: vehicleIdLabel.frame.origin.x + driverLabel.frame.width, y: driverLabel.frame.origin.y, width: textFieldWidth / 2.0 - textFieldSeparator , height: textFieldHeight))
        driver1TextField.borderStyle = .roundedRect
        driver1TextField.autocapitalizationType = .none
        driver1TextField.autocorrectionType = .no
        driver1TextField.text = "\(dID1)"
        
        
        
        driver2TextField = UITextField(frame: CGRect(x: vehicleIdLabel.frame.origin.x + driverLabel.frame.width + driver1TextField.frame.width + textFieldSeparator, y: driverLabel.frame.origin.y, width: driver1TextField.frame.width , height: textFieldHeight))
        driver2TextField.borderStyle = .roundedRect
        driver2TextField.autocapitalizationType = .none
        driver2TextField.autocorrectionType = .no
        driver2TextField.text = "\(dID2)"
        
        
        checkLocationButton = UIButton(frame: CGRect(x: labelLeftEdgeInset , y: driverLabel.frame.origin.y+textFieldSeparator * 6.0, width: view.frame.width / 3.0, height: 30))
        checkLocationButton.addTarget(self, action: #selector(locationButtonPressed), for: .touchUpInside)
        checkLocationButton.setTitle("Location", for: .normal)
        checkLocationButton.setTitleColor(.orange, for: .normal)

        
        sendEventButton = UIButton(frame: CGRect(x: checkLocationButton.frame.origin.x + checkLocationButton.frame.width + textFieldSeparator * 3.5, y: driverLabel.frame.origin.y+textFieldSeparator * 6.0, width: view.frame.width / 2.0, height: 30))
//        sendEventButton.center = CGPoint(x: view.center.x, y: sendEventButton.center.y)
        sendEventButton.setTitle("Send Information", for: .normal)
        sendEventButton.setTitleColor(.orange, for: .normal)
        sendEventButton.setTitleColor(.lightGray, for: .highlighted)
        sendEventButton.addTarget(self, action: #selector(sendAddressButtonWasPressed), for: .touchUpInside)
        
        
        resultLabel = UILabel(frame: CGRect(x: sendEventButton.frame.origin.x, y: sendEventButton.frame.origin.y + sendEventButton.frame.height - 10.0, width: sendEventButton.frame.width, height: 30))
        resultLabel.text = ""
//        resultLabel.center.x = sendEventButton.center.x
        resultLabel.textAlignment = .center
        resultLabel.textColor =  UIColor(red: 221.0/255.0, green: 219.0/255.0, blue: 215.0/255.0, alpha: 1.0)
        
        currentHistorySegmentControl = UISegmentedControl(items: ["Current Info", "History"])
        currentHistorySegmentControl.tintColor = .orange
        currentHistorySegmentControl.frame = CGRect(x: 0, y: sendEventButton.frame.origin.y + sendEventButton.frame.height + 20, width: view.frame.width / 2.0, height: 30)
        currentHistorySegmentControl.center = CGPoint(x: view.center.x, y: currentHistorySegmentControl.center.y)
        
        
        clearTextViewButton = UIButton(frame: CGRect(x: currentHistorySegmentControl.frame.origin.x + currentHistorySegmentControl.frame.width + textFieldSeparator, y: currentHistorySegmentControl.frame.origin.y, width: 60, height: 30))
        clearTextViewButton.addTarget(self, action: #selector(clearTextFieldButtonPressed), for: .touchUpInside)
        clearTextViewButton.setTitle("Clear", for: .normal)
        clearTextViewButton.setTitleColor(.lightGray, for: .normal)
        clearTextViewButton.isHidden = true
        

        
        updateHistoryTextView = UITextView(frame: CGRect(x: 0, y: currentHistorySegmentControl.frame.origin.y + currentHistorySegmentControl.frame.height + 10, width: view.frame.width * 0.9, height: view.frame.height - currentHistorySegmentControl.frame.origin.y - vehiclePicker.frame.height))
        updateHistoryTextView.center = CGPoint(x: view.center.x, y: updateHistoryTextView.center.y)
        updateHistoryTextView.isEditable = false
        updateHistoryTextView.font = UIFont.systemFont(ofSize: 16)
        updateHistoryTextView.textAlignment = .center
        updateHistoryTextView.isScrollEnabled = true
        

        
        currentHistorySegmentControl.addTarget(self, action:  #selector(segmentChanged), for: .valueChanged)
        

        
        view.addSubview(sendEventButton)
        view.addSubview(bikeNumLabel)
        view.addSubview(bikeNumTextField)
        view.addSubview(brokenbikeNumLabel)
        view.addSubview(brokenbikeNumTextField)
        view.addSubview(currentHistorySegmentControl)
        view.addSubview(updateHistoryTextView)
        view.addSubview(vehicleIdLabel)
        view.addSubview(vehiclePicker)
        view.addSubview(vehicleIdTextField)
        view.addSubview(driverLabel)
        view.addSubview(driver1TextField)
        view.addSubview(driver2TextField)
        view.addSubview(checkLocationButton)
        view.addSubview(clearTextViewButton)
        view.addSubview(resultLabel)
        
    }
    //** clear the content in updateHistoryTextView **//
    func clearTextFieldButtonPressed(){
        updateHistoryTextView.text = ""
        eventDescriptions = [String]()
        events = []
    
    }
    
    
    func segmentChanged()
    {
        switch currentHistorySegmentControl.selectedSegmentIndex{
        case 0:
            var vInfo = ""
            let url2 = URL(string: "http://ec2-54-196-202-203.compute-1.amazonaws.com/vID/\(vID)")!
            do{
                vInfo = try String(contentsOf: url2)
                
            }catch let error as NSError {
                vInfo = "Oops, something is wrong. Did you sign in correctly?"
                print("Error: \(error)")
            }

            updateHistoryTextView.text = vInfo
            clearTextViewButton.isHidden = true
        case 1:
            updateHistoryTextView.text = eventDescriptions.joined(separator: "\n")
            clearTextViewButton.isHidden = false
        default:
            break
        }
        
    }
    
    
    //** when driver press the location button, pop up a new viewcontroller **//
    func locationButtonPressed(){
        let locationViewController = LocationViewController()
        
        navigationController?.pushViewController(locationViewController, animated: true)
    }
    
    //** when driver press the send address button, update the database**//
    func sendAddressButtonWasPressed(){
        /// Unwrap the text values from our textfields
        if let number = bikeNumTextField.text, let brokennumber = brokenbikeNumTextField.text, let vehicleID = vehicleIdTextField.text, let driverID1 = driver1TextField.text, let driverID2 = driver2TextField.text{
            
            /// Check to make sure none of the text field values are blank
            if number == "" || brokennumber == "" || vehicleID == "0" || driverID1 == "" || driverID2 == "" {
                
                /// Display an alert when the user doesn't enter in all required info
                let alertController = UIAlertController(title: "Empty", message: "Please fill all fields", preferredStyle: .alert)
                
                let okAction = UIAlertAction(title: "OK", style: .default, handler: { (_) in
                    alertController.dismiss(animated: true, completion: nil)
                })
                
                alertController.addAction(okAction)
                present(alertController, animated: true, completion: nil)
                
                /// Since the user didn't enter all required info, we can return and dont have to adjust our student info
                return
            }
            
            /// Initialize a new event object and add it to our array of events
            vID = Int(vehicleID)!
            dID1 = driverID1
            dID2 = driverID2
            vBike = Int(number)!
            vBikeBroken = Int(brokennumber)!

            
            /// Send to server
            var contents = ""
            vlatitude = "40.720498"
            vlongitude = "-73.907929"
            let url = URL(string: "http://ec2-54-196-202-203.compute-1.amazonaws.com/updateVehicleInfo?vid=\(vID)&dID1=\(dID1)&dID2=\(dID2)&vBike=\(vBike)&lati=\(vlatitude)&longi=\(vlongitude)&vBikeBroken=\(vBikeBroken)")!
            do{
                contents = try String(contentsOf: url)

            }catch let error as NSError {
                contents = "\(error)"
                print("Error: \(error)")
            }

            resultLabel.text = "\(contents)"
            
            if !contents.contains("No vehicle"){
                let newEvent = Event(number:number, vID: vehicleID, dID1: driverID1, dID2: driverID2, vBikeBroken: brokennumber)
                events.append(newEvent)
                
            }

        
            
            /// Gather all event descriptions into an array
            eventDescriptions = [String]()
            for event in events {
                eventDescriptions.append(event.description())
            }
            
            /// Join the descriptions together, adding a newline character in between descriptions
//            updateHistoryTextView.text = eventDescriptions.joined(separator: "\n")
            segmentChanged()
        }
        
//        /// Clear text fields for next entry
//        bikeNumTextField.text = ""
        
    }
    

    /** set up the model for vehiclePickerview and vehicle_dic. vehicle_dic [vehicleID] contains all info associated with this particular vehicleID **/
    func fetchVehicles(){
        var api = FetchVehiclesAPI()
        api.fetchVehicles(){
            (vehicle_dic: Dictionary<Int,Dictionary<String,Any>>) in
            self.vehicle_dic = vehicle_dic
            //            self.tableView.reloadData()
            
            DispatchQueue.main.sync {
                self.vehiclePicker.reloadAllComponents()
                
            }
            
        }
        api.fetchVehiclesList(){
            (vehicleList: [Int]) in
            self.vehiclePickerData = vehicleList
            //            self.tableView.reloadData()
            
                        DispatchQueue.main.sync {
                            self.vehiclePicker.reloadAllComponents()
            
                        }
            
        }
    }
    /**  UIPickerView datasource method: number of components is 1 **/
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    
    /**  UIPickerView datasource method: number of rows in component is the number of vehiclePickerData **/

    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return vehiclePickerData.count
    }
    /**  UIPickerView datasource method: populate each row in pickerView **/
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        let tempvID: Int = vehiclePickerData[row]
        let v = vehicle_dic[tempvID]
        var vehicleName = ""
        var capacity = 0
        if let vvName = v?["vName"] as? String {
            vehicleName = vvName
        }
        if let ccapacity = v?["capacity"] as? Int {
            capacity = ccapacity
        }
        
        
       
        return "\(tempvID) \(vehicleName), Capacity \(capacity) "

    }
    /** after selecting, disappear**/
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        
        let tempvID: Int = vehiclePickerData[row]
        let v = vehicle_dic[tempvID]
        var bikeNum = 0
        
        if let vvName = v?["vName"] as? String {
            vName = vvName
        }

        if let bbikeNum = v?["vBike"] as? Int {
            bikeNum = bbikeNum
            vBike = bikeNum
        }
        
        if let bbrokenbikeNum = v?["vBikeBroken"] as? Int {
            vBikeBroken = bbrokenbikeNum
        }
        
        
        self.vehicleIdTextField.text = "\(vehiclePickerData[row])";
        self.bikeNumTextField.text = "\(vBike)"
        self.brokenbikeNumTextField.text = "\(vBikeBroken)"
        vehiclePicker.isHidden = true
//        vID = vehiclePickerData[row]
    }
    

    /** If the user is about to edit the textfield, show the vehiclePicker and disables editing **/
    func textFieldShouldBeginEditing(_ textField: UITextField) -> Bool {
        vehiclePicker.isHidden = false
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
