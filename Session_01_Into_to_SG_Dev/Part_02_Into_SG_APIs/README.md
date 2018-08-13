# Introduction to Shotgun APIs

An introduction to the various APIs that are available to Shotgun developers. 

## Contents

* **data_management.pdf**: The full deck for this session as presented at 
  dev day in pdf form.

* **ami_demo.py**: An example web service for handling AMI executions

* **example_ami_structure.py**: A Flask request object's form converted to a 
  dict to help show the AMI data structure
  
* **version_create_demo.py**: A python API example that:
  * Connects to a Shotgun site via script key
  * Finds entities using simple and compound filters
  * Create a **Version** entry linked to the found entities
  * Update the status on the created Version
  * Upload media to be associated with the Version

## Resources

* [Shotgun Developer site](http://developer.shotgunsoftware.com/)
* [Python API Github repo](https://github.com/shotgunsoftware/python-api)
* [Python API Docs](http://developer.shotgunsoftware.com/python-api/)
* [Rest API Docs](http://developer.shotgunsoftware.com/rest-api/)
* [Rest API Webinar](https://youtu.be/3xPPj2pbHVQ)
* [Shotgun Event Daemon Git Repo](https://github.com/shotgunsoftware/shotgunEvents)
* [Shotgun Event Daemon docs](https://github.com/shotgunsoftware/shotgunEvents/wiki)
* [AMI Doc](https://support.shotgunsoftware.com/hc/en-us/articles/219031318-Creating-custom-Action-Menu-Items)
