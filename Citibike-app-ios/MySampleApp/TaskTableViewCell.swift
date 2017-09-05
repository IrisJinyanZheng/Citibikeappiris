//
//  TaskTableViewCell.swift
//  MySampleApp
//
//  Created by Shangdi Yu on 6/12/17.
//
//

import UIKit

class TaskTableViewCell: UITableViewCell {
    
    /** task description **/
    @IBOutlet weak var TaskDesTextView: UITextView!
    /** taskID **/
    @IBOutlet weak var TaskIDLabel: UILabel!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }
    
    
    

}
