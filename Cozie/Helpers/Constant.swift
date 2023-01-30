//
//  Constant.swift
//  Cozie
//
//  Created by Square Infosoft on 28/12/21.
//  Copyright © 2021 Federico Tartarini. All rights reserved.
//

import UIKit

let defaultFromTime = Calendar.current.date(bySettingHour: 8, minute: 0, second: 0, of: Date()) ?? Date()
let defaultToTime = Calendar.current.date(bySettingHour: 18, minute: 0, second: 0, of: Date()) ?? Date()
let defaultNotificationFrq = Calendar.current.date(bySettingHour: 1, minute: 0, second: 0, of: Date()) ?? Date()
let defaultExperimentID = "AppleStore"
let defaultParticipantID = "ExternalTester"

let primaryColour = UIColor(named: "primaryColour")

let imgGithub = "githubLogo"
let imgBudsLab = "budsLabIcon"
let imgDownload = "downloadData"
let folderName = "Cozie"

let AWSWriteURL = "https://a1oncqr7jc.execute-api.ap-southeast-1.amazonaws.com/default/cozie-apple-write-influx"
let AWSReadURL = "https://7u940359sb.execute-api.ap-southeast-1.amazonaws.com/default/cozie-apple-read-influx"
let AWSWriteAPIKey = "g8aXeu2XnM8I3tKyezikC1aOQT6eSiMFVt6WnzLf"
let AWSReadAPIKey = "TZvrVXBuEw2ChLyWHTxdp6sdH15YiNFb73Sbc63N"

let OneSignalAppID = "e5d2f90b-c2a7-4709-ae0f-9888de4a005b"
