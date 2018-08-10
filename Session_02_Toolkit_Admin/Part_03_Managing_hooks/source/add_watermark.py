import sgtk

# for this simple example, we'll just use a hardcoded watermark image.
WATERMARK = "/tmp/resources/watermark.png"

# get the base class to use for the hook. this will process the hook
# specification in the config file and return the appropriate base class
HookBaseClass = sgtk.get_hook_baseclass()

class OpenWithWatermarkAction(HookBaseClass):

    # override the base class _open_file method. this could be considered
    # dangerous since this is a protected method. a better approach may have
    # been to override the execute_action method itself. hopefully this gets
    # the point across though
    def _open_file(self, path, sg_publish_data):

        # call the base class file open method to open the publish file
        super(OpenWithWatermarkAction, self)._open_file(
            path,
            sg_publish_data
        )

        # now add the watermark as a new layer
        self._place_file(WATERMARK, sg_publish_data)