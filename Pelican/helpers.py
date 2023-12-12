from django.conf import settings
from django.shortcuts import redirect

def login_prohibited(view_function):
   
    """
    Decorator for view functions to prevent logged-in users from accessing certain views.
    
    This decorator is useful for views that should only be accessible to users who are not logged in,
    such as login or sign-up pages. 
    
    When a logged-in user tries to access a view protected by this decorator,
    they are redirected to a specified URL.
    
    Parameters:
    - view_function: The view function that this decorator is applied to.
    """

    def modified_view_function(request):
        """
        Inner function that modifies the behavior of the decorated view.

        Checks if the user is logged in. 
        If the user is logged in, 
        they are redirected to a URL specified in Django's settings 
        (settings.REDIRECT_URL_WHEN_LOGGED_IN). 
        If not, 
        the original view is executed as normal.

        Parameters:
        - request: The HTTP request object.
        """
     
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function