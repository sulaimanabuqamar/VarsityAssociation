
class GenderSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Access request.session and set it to a global variable
        team_gender=request.session.get('team_gender', 'Men')        
        if team_gender=='Women':
            request.session['team_gender']='Women' 
        else:
            request.session['team_gender']='Men'

        response = self.get_response(request)

        return response