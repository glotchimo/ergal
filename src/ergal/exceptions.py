""" ERGAL exceptions. """


class HandlerException(Exception):
    """ Base Handler exception class. """
    def __init__(self, profile, context):
        """ Initialize HandlerException class.

        HandlerException is to be raised whenever an issues arises
        regarding the handling of an API.
        
        """
        msg = "Profile: {profile} | Context: {context}".format(
            profile=profile,
            context=context)
        super(HandlerException, self).__init__(msg)

        self.profile = profile
        self.context = context
    
    def __str__(self):
        return str(self.context)


class ProfileException(Exception):
    """ Base Profile exception class. """
    def __init__(self, profile, context):
        """ Initialize ProfileException class.

        ProfileException is to be raised whenever an issue arises
        regarding the creation, storage, or access of an API profile.
        
        """
        msg = "Profile: {profile} | Context: {context}".format(
            profile=profile,
            context=context
        )
        super(ProfileException, self).__init__(msg)

        self.profile = profile
        self.context = context

    def __str__(self):
        return str(self.context)