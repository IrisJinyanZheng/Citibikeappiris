//
//  BreakViewController.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 7/19/17.
//
//

import UIKit

//var endTime = NSDate()

class BreakViewController: UIViewController {
    /** Pressed if the driver wants to take a lunch break **/
    @IBOutlet weak var lunchBreakButton: UIButton!
    /** Pressed if the driver wants to take a 15 min short break**/
    @IBOutlet weak var shortBreakButton: UIButton!
    
    @IBOutlet weak var successLabel: UILabel!
    
    var successText = "You are on break! You can finish the break in 'Task' page by clicking the break task and click 'Complete'"
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        lunchBreakButton.layer.cornerRadius = lunchBreakButton.frame.height / 2.0
        lunchBreakButton.addTarget(self, action: #selector(lunchBreakButtonPressed), for: .touchUpInside)
        lunchBreakButton.frame.origin.x = view.center.x - lunchBreakButton.frame.width / 2.0
        
        shortBreakButton.layer.cornerRadius = shortBreakButton.frame.height / 2.0
        shortBreakButton.addTarget(self, action: #selector(shortBreakButtonPressed), for: .touchUpInside)
        shortBreakButton.frame.origin.x = view.center.x   - shortBreakButton.frame.width / 2.0

        
        successLabel.text = ""
        successLabel.frame.origin.x = view.center.x   - successLabel.frame.width / 2.0
        
        // Do any additional setup after loading the view.
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
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
