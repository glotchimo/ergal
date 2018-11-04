""" ERGAL exceptions. """


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

