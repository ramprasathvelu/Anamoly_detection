# Anamoly_detection
An AI-powered real-time security system that detects suspicious human activity in restricted areas using YOLOv8 and NLP. It analyzes live CCTV feeds and instantly sends SMS and email alerts with image evidence via Twilio and SMTP, ensuring fast response and enhanced perimeter safety.

This project presents an AI-powered real-time security monitoring system designed to automatically detect and report suspicious human activities in restricted zones. It integrates Computer Vision and Natural Language Processing (NLP) techniques to enhance perimeter safety and reduce manual monitoring efforts.

The system operates by continuously analyzing live video streams from CCTV cameras using the YOLOv8 deep learning model, one of the most advanced and efficient object detection algorithms. YOLOv8 identifies humans in each frame with high accuracy and speed. Once a person is detected, their position is compared with predefined restricted zones, which are dynamically configured as polygonal regions. If an intrusion is detected, the system classifies it as an anomaly event.

When an anomaly occurs, the system automatically triggers an alert mechanism that sends real-time notifications via SMS and email using the Twilio API and SMTP protocol. These alerts include visual evidence of the event, allowing security personnel to take immediate action even when they are not physically present.

To ensure reliability and minimize false alarms, NLP-based validation is implemented to analyze the context of the detected event. This feature significantly improves decision accuracy by distinguishing between harmless activity and genuine security breaches. All detection events are logged in both .CSV and .JSON formats for future auditing and analysis.

This intelligent automation ensures faster incident response, zero false positives, and 24/7 continuous surveillance. The system can be deployed in various real-world applications such as factories, research laboratories, warehouses, government facilities, and military bases, where maintaining security and restricted access is critical.

Overall, this project demonstrates how combining modern AI, IoT, and communication technologies can create a robust, scalable, and real-time anomaly detection framework that enhances safety, reduces human intervention, and provides immediate alerts during potential perimeter breaches.


Important>>>
1.change email id and respective Auth pass 
2 login twilio and use that sid , pass , duplicate number .
3.In terminal type "python run.py" to run the program.
