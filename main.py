KEEP_RUNNING: bool = True
STUDENT_DB: dict = dict()
# options: '' == not def, 'add_student' == cmd add student run
APP_STATE: str = ''
IDS: list[int] = []
COURSES_DB: dict = dict()
COURSES_DB['Python'] = 0  # nr of point submissions
COURSES_DB['DSA'] = 0
COURSES_DB['Databases'] = 0
COURSES_DB['Flask'] = 0
COURSES_MAX_POINTS = [600, 400, 480, 550]


import numpy as np
from operator import itemgetter


def _get_new_id():
    global IDS
    new_id = max(IDS) + 1
    IDS.append(new_id)
    return new_id


def valid_email(e: str):
    if '@' not in e:
        return False
    else:
        ep = e.split('@')
        try:
            if len(ep[0]) == 0:
                return False
            if '.' not in ep[1]:
                return False
        except Exception:
            return False
    return True


def valid_name(n: str):
    allowed_char = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-' "
    if len(n) < 2:
        return False
    for l in n:
        if l not in allowed_char:
            return False
    if n[0] in ["'", "-"] or n[-1] in ["'", "-"]:
        return False
    if "''" in n \
        or "--" in n \
        or "'-" in n \
        or "-'" in n:
        return False
    return True


def _parse_student(s: str, debug=False):
    email = s.split(' ')[-1]
    names = s[:-len(email)-1]
    first_n = names.split(' ')[0]
    last_n = names[len(first_n)+1:]
    parsed_data = []
    if debug:
        print(repr(names))
        print(repr(email))
        print(repr(first_n))
        print(repr(last_n))

    error_l = []
    if not valid_name(first_n):
        error_l.append('Incorrect first name.')
    if not valid_name(last_n):
        error_l.append('Incorrect last name.')
    if not valid_email(email):
        error_l.append('Incorrect email.')
    res_d = dict()
    res_d['credentials'] = [first_n, last_n, email]
    if error_l:
        res_d['errors'] = error_l
    return res_d

    # check email


def _parse_points(s: str):
    global STUDENT_DB
    res_d = dict()
    s_l = s.split(' ')
    i_l = []

    try:
        id_ = int(s_l[0])
        kl = list(STUDENT_DB.keys())
        if id_ < 0 or id_ >= len(kl):
            raise ValueError('No student is found for id=' + s_l[0])
    except Exception:
        raise ValueError('No student is found for id=' + s_l[0])

    if len(s_l) != 5:
        raise ValueError('Incorrect points format.')
    try:
        for e in s_l:
            i = int(e)
            if i < 0:
                raise Exception()
            i_l.append(i)
    except Exception:
        raise ValueError('Incorrect points format')

    for k,d in STUDENT_DB.items():
        if d['id'] == i_l[0]:
            res_d['email'] = d['email']
            res_d['points'] = i_l[1:]
            return res_d

    raise ValueError('No student is found for id=' + str(i_l[0]))

def calc_stats():
    """
    points: [Py,DS, Db, Fl]
    :return:
    """
    global COURSES_DB
    global STUDENT_DB

    cv = 0
    all_nan = False
    for k,v in COURSES_DB.items():
        cv = cv + v
    if cv == 0:
        all_nan = True

    popular = np.array([0, 0, 0, 0])
    total_points = np.array([0, 0, 0, 0])  # over all students
    for email, s in STUDENT_DB.items():
        # popularity
        p = np.array(s['points'])
        p_ = np.array(p > 0, dtype=int)
        popular = popular + p_

        # total points
        total_points = total_points + p

    res_d = dict()

    # popular
    ind_most_pop = np.where(popular == max(popular))[0]
    ind_least_pop = np.where(popular == min(popular))[0]

    # activity
    activity = []
    for cn, point_submissions in COURSES_DB.items():
        activity.append(point_submissions)
    ind_activity_max = np.where(np.array(activity) == np.nanmax(activity))[0]
    ind_activity_mix = np.where(np.array(activity) == np.nanmin(activity))[0]

    cn_list = list(COURSES_DB.keys())
    diff_v = []
    for i in range(len(cn_list)):
        point_sub = COURSES_DB[cn_list[i]]
        total_point = total_points[i]

        if point_sub == 0:
            aver = np.nan
        else:
            aver = total_point / point_sub

        # try:
        #     aver = total_point/point_sub
        # except ZeroDivisionError:
        #     aver = np.nan

        diff_v.append(aver)
    # print('in calc_stats', diff_v)
    ind_easy = np.where(np.array(diff_v) == max(diff_v))[0]
    ind_hard = np.where(np.array(diff_v) == min(diff_v))[0]
    # print(ind_easy)

    return ind_most_pop, ind_least_pop, ind_activity_max, ind_activity_mix, ind_easy, ind_hard, all_nan


def _ind_to_course_n(i: int) -> str:
    global COURSES_DB
    cn = list(COURSES_DB.keys())
    # print('in _ind_to_course_n', i, cn)
    return cn[i]


def print_stats():
    ind_most_pop, ind_least_pop, ind_activity_max, ind_activity_mix, ind_easy, ind_hard, all_nan = calc_stats()
    # print(ind_most_pop, ind_least_pop, ind_activity_max, ind_activity_mix, ind_easy, ind_hard, all_nan)

    msg_dict: dict = dict()
    msg_dict['Most popular'] = ''
    msg_dict['Least popular'] = ''
    msg_dict['Highest activity'] = ''
    msg_dict['Lowest activity'] = ''
    msg_dict['Easiest course'] = ''
    msg_dict['Hardest course'] = ''

    if all_nan:
        for k,v in msg_dict.items():
            print(k+': '+ 'n/a')
    else:
        # most pop
        for i, ind in enumerate(ind_most_pop):
            if i==0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Most popular'] = msg_dict['Most popular'] + msg

        # least pop
        ind_least_pop_ = [ind for ind in ind_least_pop if ind not in ind_most_pop]
        if len(ind_least_pop_) == 0:
            msg_dict['Least popular'] = ': n/a'
        for i, ind in enumerate(ind_least_pop_):
            if i == 0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Least popular'] = msg_dict['Least popular'] + msg

        # ind_activity max
        for i, ind in enumerate(ind_activity_max):
            if i==0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Highest activity'] = msg_dict['Highest activity'] + msg

        ind_activity_mix_ = [ind for ind in ind_activity_mix if ind not in ind_activity_max]
        if len(ind_activity_mix_) == 0:
            msg_dict['Lowest activity'] = ': n/a'
        for i, ind in enumerate(ind_activity_mix_):
            if i == 0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Lowest activity'] = msg_dict['Lowest activity'] + msg

        # diff
        for i, ind in enumerate(ind_easy):
            if i==0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Easiest course'] = msg_dict['Easiest course'] + msg

        ind_hard_ = [ind for ind in ind_hard if ind not in ind_easy]
        if len(ind_hard_) == 0:
            msg_dict['LHardest course'] = ': n/a'
        for i, ind in enumerate(ind_hard_):
            if i == 0:
                msg = ': ' + _ind_to_course_n(ind)
            else:
                msg = ', ' + _ind_to_course_n(ind)
            msg_dict['Hardest course'] = msg_dict['Hardest course'] + msg

        for k,v in msg_dict.items():
            print(k + v)

def _create_tuples_for_sorting(course_idx: int):
    global STUDENT_DB
    tuples_list = []
    for k,v in STUDENT_DB.items():
        tuples_list.append((k, v['points'][course_idx], v['id']))
    # multisort(list(student_objects), (('grade', True), ('age', False)))
    tuples_list_s = multisort(tuples_list, specs=((1,True),(2,False)))
    # tuples_list_s = sorted(tuples_list, key=itemgetter(1, 2), reverse=True)
    return tuples_list_s  # (email, course_points, id)

def multisort(xs, specs):
    for key, reverse in reversed(specs):
        xs.sort(key=itemgetter(key), reverse=reverse)
    return xs



def _parse_course(s: str):
    global COURSES_DB
    global STUDENT_DB
    global COURSES_MAX_POINTS
    cn_l = list(COURSES_DB.keys())
    cn_l_lower = [cn.lower() for cn in cn_l]
    if s.lower() not in cn_l_lower:
        print('Unknown course.')
    else:
        course_idx = cn_l_lower.index(s.lower())
        print(s)
        print('id \tpoints \tcompleted')
        l_s = _create_tuples_for_sorting(course_idx)
        # for i in range(min([3, len(l_s)])):
        for i in range(len(l_s)):
            l = l_s[i]
            compl = round(l[1]/COURSES_MAX_POINTS[course_idx]*100, 1)
            if l[1] == 0:
                pass
            else:
                print(str(l[2]) + '\t' + str(l[1]) + '\t' + str(compl) + '%')


def _gen_notifications():
    global STUDENT_DB
    global COURSES_MAX_POINTS
    global COURSES_DB
    notified_emails = []
    for email, sd in STUDENT_DB.items():
        passed = sd['passed']
        p_l = sd['points']
        for i, p in enumerate(p_l):
            if p >= COURSES_MAX_POINTS[i]:
                passed[i] = True
    cn_l = list(COURSES_DB.keys())
    for email, sd in STUDENT_DB.items():
        for i, cn in enumerate(cn_l):
            if sd['passed'][i] and not sd['notified'][i]:
                _send_notification(sd, email, cn)
                sd['notified'][i] = True
                notified_emails.append(email)

    print('Total ' + str(len(set(notified_emails))) + ' students have been notified.')


def _send_notification(sd: dict, email: str, cn: str):
    print('To: '+email)
    print('Re: Your Learning Progress')
    print('Hello, ' + sd['first'] + ' ' +sd['last'] + '! You have accomplished our ' + cn + ' course!')

###################################
def _close_app():
    global KEEP_RUNNING
    KEEP_RUNNING = False
    print('Bye!')


# def _empty_line_resp():
#     print('No input in response.')

def _add_student():
    global APP_STATE

    print("Enter student credentials or 'back' to return.")
    APP_STATE = 'add_student'
    # print("Enter student credentials or 'back' to return:")
    # student_str = input()

def _add_points():
    global APP_STATE
    APP_STATE = 'add_points'
    print("Enter an id and points or 'back' to return:")

def _go_back():
    global STUDENT_DB
    global APP_STATE
    if APP_STATE == 'add_student':
        print('Total '+str(len(STUDENT_DB))+' students have been added.')
        APP_STATE = ''
    elif APP_STATE == 'add_points':
        APP_STATE = ''
    elif APP_STATE == 'find':
        APP_STATE = ''
    elif APP_STATE == 'stats':
        APP_STATE = ''
    else:
        print("Enter 'exit' to exit the program.")


def _list_students():
    global STUDENT_DB
    if len(STUDENT_DB) == 0:
        print('No students found.')
    else:
        print('Students:')
        for k,d in STUDENT_DB.items():
            print(d['id'])

def _find():
    global APP_STATE
    APP_STATE = 'find'
    print("Enter an id or 'back' to return.")

def _stats():
    global APP_STATE
    APP_STATE = 'stats'
    print("Type the name of a course to see details or 'back' to quit:")
    print_stats()


def _notify():
    global APP_STATE
    APP_STATE = 'notify'
    _gen_notifications()


def _init_cmds() -> dict:
    d = dict()
    d['exit'] = _close_app
    d['add students'] = _add_student
    d['back'] = _go_back
    d['list'] = _list_students
    d['add points'] = _add_points
    d['find'] = _find
    d['statistics'] = _stats
    d['notify'] = _notify
    # d[''] = _empty_line_resp
    return d


def _add_student_to_db(fn, ln, email):
    global STUDENT_DB
    if email in STUDENT_DB:
        raise KeyError('email_duplicate')
    sd = dict()
    sd['email'] = email
    sd['first'] = fn
    sd['last'] = ln
    sd['id'] = len(STUDENT_DB)
    sd['points'] = [0, 0, 0, 0]
    sd['passed'] = [False, False, False, False]
    sd['notified'] = [False, False, False, False]
    STUDENT_DB[email] = sd


def _add_points_to_db(emial, p_l):
    global STUDENT_DB
    global COURSES_DB
    sd = STUDENT_DB[emial]
    if 'points' in sd:
        prev = sd['points']
        new_p = []
        for i in range(len(prev)):
            new_p.append(prev[i]+p_l[i])
        sd['points'] = new_p
    else:
        sd['points'] = p_l

    c_db_k_list = list(COURSES_DB.keys())
    for i in range(len(c_db_k_list)):
        p = p_l[i]
        if p > 0:  # assignment submissions
            COURSES_DB[c_db_k_list[i]] = COURSES_DB[c_db_k_list[i]] + 1


def _find_student(rs: str):
    global STUDENT_DB
    k = list(STUDENT_DB.keys())
    if len(rs)>1:
        s = rs.lstrip('0')
    else:
        s=rs

    try:
        email = STUDENT_DB[k[int(s)]]['email']
    except (IndexError, ValueError):
        print('No student is found for id='+rs+'.')
    else:
        p_l = STUDENT_DB[email]['points']
        print(s+' points: Python='+str(p_l[0])
              + '; DSA='+str(p_l[1])
              + '; Databases='+str(p_l[2])
              + '; Flask='+str(p_l[3]))

def app_loop():
    global KEEP_RUNNING
    global APP_STATE
    cmds = _init_cmds()

    while KEEP_RUNNING:
        rui = input()
        ui = rui.rstrip()
        if ui:  # not empty
            if APP_STATE == 'add_student' and ui != 'back':
                res_d = _parse_student(ui)
                if 'errors' in res_d:
                    if len(res_d['errors']) > 1:
                        print('Incorrect credentials.')
                    else:
                        print(res_d['errors'][0])
                else:
                    student_data = res_d['credentials']
                    try:
                        _add_student_to_db(
                            fn=student_data[0],
                            ln=student_data[1],
                            email=student_data[2]
                        )
                    except KeyError:
                        print('This email is already taken.')
                    else:
                        print('Student has been added.')
            elif APP_STATE == 'add_points' and ui != 'back':
                try:
                    res_d = _parse_points(ui)
                except ValueError as e:
                    print(e)
                else:
                    _add_points_to_db(res_d['email'], res_d['points'])
                    print('Points updated.')
            elif APP_STATE == 'find' and ui != 'back':
                _find_student(ui)
            elif APP_STATE == 'stats' and ui != 'back':
                _parse_course(ui)
            # elif APP_STATE == 'notify' and ui != 'back':
            #     pass
            else:
                try:
                    f = cmds[ui]
                    f()
                except KeyError as e:
                    print('Error: unknown command!', e)
        else:
            if APP_STATE == 'add_student':
                print('Incorrect credentials')
            if APP_STATE == 'find':
                print('No student is found for id=.')
            else:
                print('No input')

def test():
    _parse_student('jan jansen jan@jans.com')
    # testval = "j--an"
    # res = valid_name(testval)
    # print(testval, res)



if __name__ == '__main__':
    print("Learning progress tracker")

    app_loop()

    # test()
