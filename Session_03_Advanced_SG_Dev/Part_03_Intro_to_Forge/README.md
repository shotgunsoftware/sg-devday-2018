# Intro to Forge

This session provides a brief introduction to the Forge Development Platform and
how it can be integrated with Shotgun. A simple example integration is included
with code that can be used as reference.

## Contents

* **upload_to_forge.py**: A publish plugin that shows how to upload an obj model
  to Forge via the standalone (browse or drag/drop) publisher. See the `TODO` 
  items in the code to learn more about how to try it out (requires a Forge
  app client id and secret). You'll also need to drop this plugin into your 
  configuration and update the stand alone publisher settings accordingly.
  
* **web**: Source code for displaying a forge model viewer in Shotgun
  * **simple-forge-model-server.py**: A very simple python server you can use 
    for embedding a forge model viewer in SG over https. See the `TODO`s in the
    code for setup/execution instructions
  * **model_viewer.html**: The page that displays the forge model. Expects 
    a `forge_urn` query parameter. See the keynote deck for specifics.

## Resources

* Forge
  * [Forge Homepage](https://forge.autodesk.com/)
  * [Forge APIs](https://developer.autodesk.com/en/docs/)
* Toolkit
  * [Publisher Developer Docs](http://developer.shotgunsoftware.com/tk-multi-publish2)
* Miscellaneous
  * [Simple HTTPs Server](https://gist.github.com/dergachev/7028596)
  
TODO: when keynote is finished, convert to PDF and include here
