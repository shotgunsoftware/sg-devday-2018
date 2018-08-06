import sgtk

# get the base class to use for the hook. this will process the hook
# specification in the config file and return the appropriate base class
HookBaseClass = sgtk.get_hook_baseclass()


class EnsureTaskPublishPlugin(HookBaseClass):

    # override the validate method and include our new check for the task
    def validate(self, settings, item):

        # does the item have a task defined?
        if not item.context.task:
            self.logger.error(
                "Publish item '%s' does not have a task associated. "
                "Please select a task on the right for this item." % (item,)
            )
            return False

        # call the base class implementation
        return super(EnsureTaskPublishPlugin, self).validate(
            settings,
            item
        )
