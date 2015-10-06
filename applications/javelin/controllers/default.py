# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from javelin_utils import json

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # if not auth.user:
    #     redirect(URL('default', 'marketing'))
    return dict()

@auth.requires_login()
def dashboard():
    return dict(user=auth.user.first_name)

@auth.requires_login()
def search():
    return dict()

@auth.requires_login()
def events():
    return dict()

@auth.requires_login()
def messages():
    return dict()

@auth.requires_login()
def people():
    return dict()

@auth.requires_login()
def people_table():
    return dict()

@auth.requires_login()
def people_detail():
    return dict()

@auth.requires_login()
def tutoring():
    return dict()

@auth.requires_login()
def jadmin():
    return dict()

@auth.requires_login()
def main():
    return dict()
    
# def init():
#     people = [{'grade': 12, 'student_id': 100001, 'first_name': 'Edwin', 'last_name': u'McCullough'}, {'grade': 12, 'student_id': 100002, 'first_name': u'Julien', 'last_name': u'Ledner'}, {'grade': 12, 'student_id': 100003, 'first_name': u'Ryland', 'last_name': u'Bauch'}, {'grade': 12, 'student_id': 100004, 'first_name': u'Bryana', 'last_name': u'Donnelly'}, {'grade': 12, 'student_id': 100005, 'first_name': u'Gage', 'last_name': u'Turcotte'}, {'grade': 12, 'student_id': 100006, 'first_name': u'Julianne', 'last_name': u'Zemlak'}, {'grade': 12, 'student_id': 100007, 'first_name': u'Aurore', 'last_name': u'Cruickshank'}, {'grade': 12, 'student_id': 100008, 'first_name': u'Sunday', 'last_name': u'Kemmer'}, {'grade': 12, 'student_id': 100009, 'first_name': u'Nathalie', 'last_name': u'Kassulke'}, {'grade': 12, 'student_id': 100010, 'first_name': u'Jesica', 'last_name': u'McCullough'}, {'grade': 12, 'student_id': 100011, 'first_name': u'Anita', 'last_name': u'Pfannerstill'}, {'grade': 12, 'student_id': 100012, 'first_name': u'Giancarlo', 'last_name': u'Kohler'}, {'grade': 12, 'student_id': 100013, 'first_name': u'Rianna', 'last_name': u'Blanda'}, {'grade': 12, 'student_id': 100014, 'first_name': u'Westley', 'last_name': u'Eichmann'}, {'grade': 12, 'student_id': 100015, 'first_name': u'Jazlyn', 'last_name': u'Tillman'}, {'grade': 12, 'student_id': 100016, 'first_name': u'Ansel', 'last_name': u'Kuhic'}, {'grade': 12, 'student_id': 100017, 'first_name': u'Levy', 'last_name': u'Langosh'}, {'grade': 12, 'student_id': 100018, 'first_name': u'Kristie', 'last_name': u'Huel'}, {'grade': 12, 'student_id': 100019, 'first_name': u'Theron', 'last_name': u'Barrows'}, {'grade': 12, 'student_id': 100020, 'first_name': u'Albertha', 'last_name': u'Hettinger'}, {'grade': 12, 'student_id': 100021, 'first_name': u'Isaiah', 'last_name': u'Sawayn'}, {'grade': 12, 'student_id': 100022, 'first_name': u'Aarav', 'last_name': u'McClure'}, {'grade': 12, 'student_id': 100023, 'first_name': u'Laraine', 'last_name': u'Kuhlman'}, {'grade': 12, 'student_id': 100024, 'first_name': u'Dorthy', 'last_name': u'Powlowski'}, {'grade': 12, 'student_id': 100025, 'first_name': u'Fitzgerald', 'last_name': u'Kessler'}, {'grade': 12, 'student_id': 100026, 'first_name': u'Erna', 'last_name': u'Nicolas'}, {'grade': 12, 'student_id': 100027, 'first_name': u'Landen', 'last_name': u'VonRueden'}, {'grade': 12, 'student_id': 100028, 'first_name': u'Kala', 'last_name': u'Walsh'}, {'grade': 12, 'student_id': 100029, 'first_name': u'Queenie', 'last_name': u'Larson'}, {'grade': 12, 'student_id': 100030, 'first_name': u'Anthony', 'last_name': u'Hermiston'}, {'grade': 12, 'student_id': 100031, 'first_name': u'Maddux', 'last_name': u'Bode'}, {'grade': 12, 'student_id': 100032, 'first_name': u'Josephus', 'last_name': u'Stroman'}, {'grade': 12, 'student_id': 100033, 'first_name': u'Leander', 'last_name': u'McLaughlin'}, {'grade': 12, 'student_id': 100034, 'first_name': u'Malinda', 'last_name': u'Kuhlman'}, {'grade': 12, 'student_id': 100035, 'first_name': u'Ebba', 'last_name': u'Feil'}, {'grade': 12, 'student_id': 100036, 'first_name': u'Marcelina', 'last_name': u'Koch'}, {'grade': 12, 'student_id': 100037, 'first_name': u'Darell', 'last_name': u'Rempel'}, {'grade': 12, 'student_id': 100038, 'first_name': u'Zelma', 'last_name': u'Harvey'}, {'grade': 12, 'student_id': 100039, 'first_name': u'Danette', 'last_name': u'Jakubowski'}, {'grade': 12, 'student_id': 100040, 'first_name': u'Joretta', 'last_name': u'Adams'}, {'grade': 12, 'student_id': 100041, 'first_name': u'Fabiola', 'last_name': u'Greenfelder'}, {'grade': 12, 'student_id': 100042, 'first_name': u'Deja', 'last_name': u'Friesen'}, {'grade': 12, 'student_id': 100043, 'first_name': u'Kian', 'last_name': u'Jacobson'}, {'grade': 12, 'student_id': 100044, 'first_name': u'Yehuda', 'last_name': u'Green'}, {'grade': 12, 'student_id': 100045, 'first_name': u'Taurean', 'last_name': u'Nolan'}, {'grade': 12, 'student_id': 100046, 'first_name': u'Dustyn', 'last_name': u'Wunsch'}, {'grade': 12, 'student_id': 100047, 'first_name': u'Genevieve', 'last_name': u'Strosin'}, {'grade': 12, 'student_id': 100048, 'first_name': u'Junia', 'last_name': u'Kemmer'}, {'grade': 12, 'student_id': 100049, 'first_name': u'Jaheem', 'last_name': u'Yost'}, {'grade': 12, 'student_id': 100050, 'first_name': u'Myrtice', 'last_name': u'Mayer'}]
#     for p in people:
#         db.person.insert(**p)
#     return True

# def test():
#     city = 'Adonisside'
#     state = 'California'
#     zip_code = '45232'
#     addresses = [{'address': '95023 Quigley Avenue'}, {'address': '64047 Maggio Expressway'}, {'address': '329 Schuppe Village Apt. 380'}, {'address': '79982 Eben Inlet Suite 979'}, {'address': '96967 Minna Alley'}, {'address': '40806 Ortiz Well'}, {'address': '100 Shelvia Branch Apt. 899'}, {'address': '62961 Anona Port'}, {'address': '925 Grimes Avenue'}, {'address': '9310 Wintheiser Lodge Apt. 789'}, {'address': '30107 Wintheiser Via'}, {'address': '31968 Garry Bridge'}, {'address': '73593 Watsica Union'}, {'address': '557 Abram Cape Apt. 779'}, {'address': '531 DuBuque Extension'}, {'address': '36802 Almedia Gateway Apt. 344'}, {'address': '52457 Vashon Spring Suite 550'}, {'address': '890 Shoji Forest Apt. 283'}, {'address': '275 Abbie Points Apt. 333'}, {'address': '926 Maude Radial'}, {'address': '07135 Kihn Canyon Apt. 311'}, {'address': '4119 Virge Island'}, {'address': '96990 Elenora Gardens'}, {'address': '0922 Leonidas Springs'}, {'address': "7986 O'Keefe Prairie Apt. 421"}, {'address': '1213 Hilll Turnpike'}, {'address': '267 Chandra Track Apt. 698'}, {'address': '968 Thompson Fork Suite 433'}, {'address': '79566 Shirlee Village'}, {'address': '8287 Kub Wall Suite 521'}, {'address': '6223 Burgess Fall Apt. 232'}, {'address': '2030 Tari Forks'}, {'address': '0841 Lynch Fall Apt. 772'}, {'address': '59982 Krajcik Forest'}, {'address': '897 Gibson Via Suite 100'}, {'address': '2242 Martez Estates Suite 844'}, {'address': '37772 Javier Cliff'}, {'address': '11609 Codi Knoll Apt. 704'}, {'address': '5693 Taraji Spurs Suite 985'}, {'address': '6995 Kertzmann Glens Suite 239'}, {'address': '108 Reginal Islands Suite 104'}, {'address': '974 Jenkins Circles Suite 757'}, {'address': '0739 Gabriella Divide'}, {'address': '5305 Giovani Row Apt. 838'}, {'address': '341 Lona Way Suite 108'}, {'address': '942 Leonce Gateway'}, {'address': '015 Beatty Well Suite 199'}, {'address': '2695 George Groves'}, {'address': '6501 Pouros Knoll'}, {'address': '607 Asher Radial'}, {'address': '887 Jacobs Canyon Apt. 779'}, {'address': '17004 Lynch Wells'}, {'address': '7228 Davis Drive'}, {'address': '732 Altenwerth Track'}, {'address': "19283 O'Connell Heights Suite 787"}]
#     for i, p in enumerate(db(db.person).select()):
#         p.update_record(address=addresses[i]['address'], city=city, state=state, zip_code=zip_code)
#     return db(db.person).count()

def init():
    print "DOOOBEEEDOOO"
    return True

def marketing():
    return dict()

# def login():

#     print form.accepted

#     return dict(form=form)

# def logout():
#     return auth.logout()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0) == 'login':
        next = request.vars._next if request.vars._next and request.vars._next != '/dashboard' else '/'
        form = auth.login(onaccept=lambda form: redirect(URL('default', 'index', anchor=next)))
        # form['_ajax-form'] = ""
        # form['_ng-submit'] = "submitForm($event)"
        form['_action'] = '/user/login'
        if not 'request_reset_password' in auth.settings.actions_disabled:
            form[0].append(DIV(A('Lost your password?', _href=URL(args='request_reset_password'))))
    elif request.args(0) == 'logout':
        return auth.logout(next=URL('default', 'index'))
    elif request.args(0) == 'is_authenticated':
        response.view = 'generic.json'
        response.headers['Content-Type'] = 'application/json'
        return response.json(auth.user != None)
    else:
        redirect(URL('default', 'index'))

    # elif request.args(0)=='register':
    #     form[0].insert(-1, DIV(
    #         INPUT(_name='password_two', _type='password', _class='password form-control',
    #             requires=IS_EXPR('value==%s' % repr(request.vars.get('password', None))),
    #             _placeholder='Verify Password', error_message=auth.messages.mismatch_password),
    #             _class='form-group'))

    return dict(form=form)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
